import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from resistor_brain.brain.gnn_scorer import get_scorer

def generate_json():
    print("--- RESISTOR: Generating GPU Benchmark Candidates ---")
    
    # Get the real wild-type sequence directly from the graph
    scorer = get_scorer()
    wt_seq = scorer.wt_seq
    print(f"[INFO] Loaded Wild-Type Sequence (Length: {len(wt_seq)})")

    AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
    candidates = []

    # Generate EVERY possible single-point mutation for the whole protein
    for i, wt_aa in enumerate(wt_seq):
        pos = i + 1  # 1-based biological position
        for mut_aa in AMINO_ACIDS:
            if mut_aa != wt_aa:
                candidates.append({
                    "position": pos,
                    "mutated_aa": mut_aa
                })

    output_path = os.path.join(os.path.dirname(__file__), 'candidate_mutations.json')
    with open(output_path, 'w') as f:
        json.dump(candidates, f, indent=4)

    print(f"[SUCCESS] Generated {len(candidates)} total candidates.")
    print(f"[SUCCESS] Saved payload to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    generate_json()