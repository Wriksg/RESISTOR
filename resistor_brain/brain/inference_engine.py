import sys
import os
import json

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from resistor_brain.brain.ga_loop import GeneticAlgorithm, GAConfig
from resistor_brain.brain.gnn_scorer import get_scorer
from resistor_brain.brain.ranker import rank_candidates
from resistor_brain.brain.attribution_extractor import extract_attribution
from resistor_brain.brain.reasoning_generator import generate_reasoning

def run_inference():
    print("--- RESISTOR INFERENCE ENGINE ---")
    print("[1/4] Loading Target Structure...")
    scorer = get_scorer()
    wt_seq = scorer.wt_seq
    pocket_positions = [5, 20, 27, 46, 54, 92, 94, 98]

    print("[2/4] Running Evolutionary Search (Generating Candidates)...")
    config = GAConfig()
    config.population_size = 100
    config.generations = 10
    
    ga = GeneticAlgorithm(config, pocket_positions, wt_seq)
    population = ga.initialize_population()
    
    # Seed F98Y just to guarantee it shows up in our demo JSON output
    population[0] = "".join([c if i != 97 else 'Y' for i, c in enumerate(wt_seq)])
    
    all_seen_candidates = set()
    for gen in range(config.generations):
        population, pop_scores = ga.evolve_one_generation(population)
        for seq, _ in pop_scores:
            all_seen_candidates.add(seq)

    print("[3/4] Ranking and Formatting Candidates...")
    top_candidates = rank_candidates(all_seen_candidates, wt_seq, scorer, top_n=10)
    
    final_output = {
        "target": "S. aureus DHFR (2w9g)",
        "top_mutations": []
    }
    
    for rank, candidate in enumerate(top_candidates):
        candidate = extract_attribution(candidate, wt_seq)
        candidate = generate_reasoning(candidate)
        candidate['rank'] = rank + 1
        final_output["top_mutations"].append(candidate)

    print("[4/4] Saving Results to JSON...")
    output_path = os.path.join(os.path.dirname(__file__), '../../resistor_output.json')
    with open(output_path, 'w') as f:
        json.dump(final_output, f, indent=4)
        
    print(f"✅ SUCCESS! Final output saved to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    run_inference()