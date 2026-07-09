import random
from typing import List, Tuple

AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

# --- DUMMY CONFIG FOR PART 3 ---
class DummyConfig:
    def __init__(self):
        self.population_size = 15
        self.mutation_rate = 0.2
        self.crossover_rate = 0.7

# --- DUMMY SCORER FOR PART 3 ---
def dummy_fitness_scorer(sequence: str) -> float:
    """
    FAKE SCORER: Returns a random score between 0 and 1.
    In Part 8, we will replace this with your real GNN scoring the structural graph!
    """
    return random.uniform(0.0, 1.0)

class GeneticAlgorithm:
    def __init__(self, config, target_positions: List[int]):
        self.config = config
        self.target_positions = target_positions

    def initialize_population(self, wild_type: str) -> List[str]:
        population = [wild_type]
        for _ in range(self.config.population_size - 1):
            population.append(self.mutate(wild_type, force=True))
        return population

    def mutate(self, sequence: str, force: bool = False) -> str:
        if not force and random.random() > self.config.mutation_rate:
            return sequence
            
        seq_list = list(sequence)
        # Select 1-based biological position
        bio_pos = random.choice(self.target_positions)
        idx = bio_pos - 1 # Convert to 0-based array index
        
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
            idx = bio_pos - 1  # Convert to 0-based array index
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
                score -= 5.0
            else:
                seen.add(seq)
            penalized.append((seq, score))
        return penalized

    # --- REMOVED ESM2 AND PHYSICS FILTER FOR RESISTOR ---
    def evolve_one_generation(self, current_population: List[str]) -> Tuple[List[str], float]:
        # Score using the dummy scorer
        pop_with_scores = []
        for seq in current_population:
            final_score = dummy_fitness_scorer(seq)
            pop_with_scores.append((seq, final_score))

        # Diversity penalty
        pop_with_scores = self.apply_diversity_penalty(pop_with_scores)

        # Sort to find the best score easily
        pop_with_scores.sort(key=lambda x: x[1], reverse=True)
        best_score = pop_with_scores[0][1]

        # Elitism
        new_population = [pop_with_scores[0][0]]

        # Fill generation
        while len(new_population) < self.config.population_size:
            p1 = self.tournament_selection(pop_with_scores)
            p2 = self.tournament_selection(pop_with_scores)
            child = self.crossover(p1, p2)
            child = self.mutate(child)
            new_population.append(child)

        return new_population, best_score

if __name__ == "__main__":
    print("\n--- RESISTOR: GA Loop (AETHER Port) ---")
    config = DummyConfig()
    
    # We use the binding pocket residues from Part 1 as our target positions!
    target_positions = [5, 20, 27, 46, 54, 92, 94, 98]
    
    # A fake 157-length protein (just to test the math, since DHFR is 157 aa long)
    wild_type_seq = "A" * 157  
    
    ga = GeneticAlgorithm(config, target_positions)
    population = ga.initialize_population(wild_type_seq)
    
    generations = 10
    print("Starting Evolutionary Search (Dummy Scorer)...")
    for gen in range(generations):
        population, best_score = ga.evolve_one_generation(population)
        print(f"Generation {gen+1}/{generations} | Best Fitness: {best_score:.4f}")
        
    print("\n[SUCCESS] GA Loop ported successfully!")