import sys
import os
import time
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from resistor_brain.brain.gnn_scorer import get_scorer

def run_gpu_batch():
    print("--- RESISTOR: AMD ROCm GPU Batch Runner ---")
    
    # 1. Load Model
    start_load = time.time()
    scorer = get_scorer()
    print(f"[INFO] Model loaded in {time.time() - start_load:.2f} seconds.")
    print(f"[INFO] Device in use: {scorer.device}")

    # 2. Load the static JSON payload
    json_path = os.path.join(os.path.dirname(__file__), 'candidate_mutations.json')
    if not os.path.exists(json_path):
        print(f"[ERROR] Could not find {json_path}. Run generate_candidates.py first!")
        return

    with open(json_path, 'r') as f:
        payload = json.load(f)
        
    print(f"[INFO] Successfully loaded payload of {len(payload)} mutations.")

    # 3. Run Inference
    print(f"[INFO] Processing batch through the GNN...")
    start_inf = time.time()
    
    results = scorer.score_batch(payload)
    
    inf_time = time.time() - start_inf
    print(f"[SUCCESS] Batch scored in {inf_time:.4f} seconds ({(inf_time/max(1, len(payload)))*1000:.2f} ms per mutation).")
    
    # Print a small sample to verify it worked
    print("\n--- SAMPLE RESULTS (Top 5) ---")
    for i in range(min(5, len(results))):
        pos = payload[i]['position']
        aa = payload[i]['mutated_aa']
        b_delta = results[i]['binding_delta']
        s_delta = results[i]['stability_delta']
        print(f"Mut {i+1} (Pos {pos} -> {aa}): Binding \u0394 {b_delta:.4f} | Stability \u0394 {s_delta:.4f}")

if __name__ == "__main__":
    run_gpu_batch()