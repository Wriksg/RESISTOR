import os
import json
import yaml

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "target_config.yaml")
GRAPH_PATH = os.path.join(BASE_DIR, "data", "processed", "residue_contact_graph.json")
OUT_PATH = os.path.join(BASE_DIR, "data", "processed", "candidate_mutations.json")

# 3-letter to 1-letter amino acid conversion
AA_MAP = {'ALA': 'A', 'CYS': 'C', 'ASP': 'D', 'GLU': 'E', 'PHE': 'F',
          'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LYS': 'K', 'LEU': 'L',
          'MET': 'M', 'ASN': 'N', 'PRO': 'P', 'GLN': 'Q', 'ARG': 'R',
          'SER': 'S', 'THR': 'T', 'VAL': 'V', 'TRP': 'W', 'TYR': 'Y'}

AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

def generate_candidates():
    print("\n--- RESISTOR: Mutation Generator ---")
    
    # Load config and graph
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    with open(GRAPH_PATH, 'r') as f:
        graph = json.load(f)
        
    binding_sites = config['binding_site_residues']
    print(f"Targeting active site residues: {binding_sites}")
    
    # Find all residues connected to the binding site in 3D space
    target_pool = set(binding_sites)
    for edge in graph['edges']:
        if edge['source'] in binding_sites:
            target_pool.add(edge['target'])
        if edge['target'] in binding_sites:
            target_pool.add(edge['source'])
            
    print(f"Found {len(target_pool)} total residues structurally touching the active site.")
    
    # Generate mutations
    candidates = []
    for node in graph['nodes']:
        if node['id'] in target_pool:
            wt_aa = AA_MAP.get(node['name'], 'A') # Convert PHE to F, etc.
            
            # Mutate to every other possible amino acid
            for mut_aa in AMINO_ACIDS:
                if mut_aa != wt_aa:
                    mutation_name = f"{wt_aa}{node['id']}{mut_aa}" # e.g., F98Y
                    candidates.append({
                        "mutation": mutation_name,
                        "position": node['id'],
                        "wild_type": wt_aa,
                        "mutated": mut_aa
                    })
                    
    # Save the candidate pool
    with open(OUT_PATH, 'w') as f:
        json.dump(candidates, f, indent=2)
        
    print(f"[SUCCESS] Generated {len(candidates)} plausible candidate mutations.")
    print(f"Saved to: {OUT_PATH}\n")

if __name__ == "__main__":
    generate_candidates()