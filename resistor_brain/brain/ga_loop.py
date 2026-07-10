import random
import json
import os
import sys
from typing import List, Tuple

# --- Add project root to python path to fix ModuleNotFoundError ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from resistor_brain.brain.gnn_scorer import get_scorer
from resistor_brain.brain.physics_penalty import calculate_fitness

AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

class GAConfig:
    def __init__(self):
        self.population_size = 50
        self.mutation_rate = 0.3
        self.crossover_rate = 0.5
        self.generations = 15

class GeneticAlgorithm:
    def __init__(self, config, target_positions: List[int], wild_type: str):
        self.config = config
        self.target_positions = target_positions
        self.wild_type = wild_type

    def initialize_population(self) -> List[str]:
        population = [self.wild_type]
        for _ in range(self.config.population_size - 1):
            population.append(self.mutate(self.wild_type, force=True))
        return population

    def mutate(self, sequence: str, force: bool = False) -> str:
        if not force and random.random() > self.config.mutation_rate:
            return sequence
            
        seq_list = list(sequence)
        bio_pos = random.choice(self.target_positions)
        idx = bio_pos - 1 
        
        new_aa = random.choice(AMINO_ACIDS)
        while new_aa == seq_list[idx]:
            new_aa = random.choice(AMINO_ACIDS)
            
        seq_list[idx] = new_aa
        return "".join(seq_list)

    def crossover(self, parent1: str, parent2: str) -> str:
        if random.random() > self.config.crossover_rate:
            return parent1 if random.random() > 0.5 else parent2
            
        child_list = list(parent1)
        for bio_pos in self.target_positions:
            idx = bio_pos - 1 
            if random.random() > 0.5:
                child_list[idx] = parent2[idx]
                
        return "".join(child_list)

    def tournament_selection(self, pop_with_scores: List[Tuple[str, float]], k: int = 3) -> str:
        tournament = random.sample(pop_with_scores, k)
        return max(tournament, key=lambda x: x[1])[0]

    def apply_diversity_penalty(self, pop_with_scores: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        seen = set()
        penalized = []
        for seq, score in pop_with_scores:
            if seq in seen:
                score -= 1.0 
            else:
                seen.add(seq)
            penalized.append((seq, score))
        return penalized

    def evolve_one_generation(self, current_population: List[str]) -> List[str]:
        scorer = get_scorer()
        pop_with_scores = []
        
        for seq in current_population:
            final_score = scorer.score_sequence(seq)
            pop_with_scores.append((seq, final_score))

        pop_with_scores = self.apply_diversity_penalty(pop_with_scores)

        best_candidate = max(pop_with_scores, key=lambda x: x[1])[0]
        new_population = [best_candidate]

        while len(new_population) < self.config.population_size:
            p1 = self.tournament_selection(pop_with_scores)
            p2 = self.tournament_selection(pop_with_scores)
            child = self.crossover(p1, p2)
            child = self.mutate(child)
            new_population.append(child)

        return new_population, pop_with_scores


# ==========================================
# EXECUTION BLOCK (Run this file to test)
# ==========================================
if __name__ == "__main__":
    THREE_TO_ONE = {
        'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
        'GLU': 'E', 'GLN': 'Q', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
        'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
        'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'
    }

    print("--- RESISTOR: Initializing Genetic Algorithm ---")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    graph_path = os.path.join(base_dir, '../../resistor_bio/data/processed/residue_contact_graph.json')
    
    with open(graph_path, 'r') as f:
        nodes = json.load(f)['nodes']
    
    wild_type_seq = "".join([THREE_TO_ONE.get(n['name'], n['name']) for n in nodes])
    print(f"[INFO] Loaded Wild-Type Sequence (Length: {len(wild_type_seq)})")
    
    pocket_positions = [5, 20, 27, 46, 54, 92, 94, 98]
    
    config = GAConfig()
    ga = GeneticAlgorithm(config, pocket_positions, wild_type_seq)
    
    population = ga.initialize_population()
    
    print("\n[INFO] Starting Evolution...")
    
    all_seen_candidates = {} 
    
    for gen in range(config.generations):
        population, pop_scores = ga.evolve_one_generation(population)
        
        scorer = get_scorer()
        for seq in population:
            if seq not in all_seen_candidates:
                all_seen_candidates[seq] = scorer.score_sequence(seq)
                
        gen_best_seq, gen_best_score = max(pop_scores, key=lambda x: x[1])
        print(f"Generation {gen+1:02d} | Best Fitness: {gen_best_score:.4f}")

    print("\n--- EVOLUTION COMPLETE ---")
    
    # Sort by true fitness
    ranked_candidates = sorted(all_seen_candidates.items(), key=lambda x: x[1], reverse=True)
    
    print("\n🏆 TOP 10 DISCOVERED MUTATIONS:")
    print("--------------------------------------------------")
    for i in range(min(10, len(ranked_candidates))):
        seq, score = ranked_candidates[i]
        
        # Build mutation string to handle both single and multi mutations
        muts = []
        for idx, (wt, mut) in enumerate(zip(wild_type_seq, seq)):
            if wt != mut:
                muts.append(f"{wt}{idx+1}{mut}")
                
        mut_str = " + ".join(muts) if muts else "WT"
        
        # Highlight F98Y specifically
        flag = "  <-- KNOWN RESISTANCE TARGET" if "F98Y" in mut_str else ""
        print(f"Rank {i+1:02d} | Mutation: {mut_str.ljust(15)} | Fitness: {score:.4f}{flag}")