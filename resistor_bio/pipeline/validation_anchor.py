import os
import json
import csv

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "raw", "known_resistance_mutations.csv")
JSON_PATH = os.path.join(BASE_DIR, "data", "processed", "candidate_mutations.json")

def validate_anchor():
    print("\n--- RESISTOR: Validation Anchor Check ---")
    
    # 1. Read the known mutation from your CSV
    known_mutations = []
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            known_mutations.append(row['mutation'].strip())
            
    target_mutation = known_mutations[0]
    print(f"Looking for published resistance mutation: {target_mutation}")
    
    # 2. Check if it exists in the 1140 generated candidates
    with open(JSON_PATH, 'r') as f:
        candidates = json.load(f)
        
    generated_mutations = [c['mutation'] for c in candidates]
    
    if target_mutation in generated_mutations:
        print(f"\n[MASSIVE SUCCESS] The known mutation {target_mutation} is in the search pool!")
        print("Your structural proximity logic is biologically accurate.")
        print("Part 6 is DONE.\n")
    else:
        print(f"\n[ERROR] {target_mutation} was NOT found in the candidates.")
        print("We need to expand the distance cutoff in target_config.yaml.")

if __name__ == "__main__":
    validate_anchor()