import sys
import os

# Ensure Python can find the root module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from resistor_brain.brain.gnn_scorer import get_scorer

print("--- Testing GNN Batch API ---")

# Load the singleton scorer
scorer = get_scorer()

# The exact payload Shrijib requested
payload = [
    {"position": 46, "mutated_aa": "Q"}, 
    {"position": 98, "mutated_aa": "Y"}
]

print(f"Sending payload: {payload}\n")

# Call the batch method
results = scorer.score_batch(payload)

print("--- BATCH RESULTS ---")
for i, res in enumerate(results):
    print(f"Mutation {i+1} ({payload[i]['mutated_aa']} at {payload[i]['position']}):")
    print(f"  Binding Delta:   {res['binding_delta']:.4f}")
    print(f"  Stability Delta: {res['stability_delta']:.4f}\n")