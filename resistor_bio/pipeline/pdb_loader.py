import os
import yaml
import numpy as np
from Bio.PDB import PDBParser

# Setup dynamic paths so it works no matter where you run it from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "target_config.yaml")
PDB_PATH = os.path.join(BASE_DIR, "data", "raw", "target_protein.pdb")

def load_config():
    with open(CONFIG_PATH, 'r') as file:
        return yaml.safe_load(file)

def parse_pdb():
    config = load_config()
    print(f"Loading {config['target_name']} (PDB: {config['pdb_id']})...")
    
    # Initialize BioPython PDB Parser
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(config['pdb_id'], PDB_PATH)
    
    # The PDB file has multiple chains. We only need Chain A for the graph.
    model = structure[0]
    chain_a = model['A']
    
    residues = []
    coords = []
    
    for residue in chain_a:
        # Skip heteroatoms (water, ions, etc.) - we ONLY want the protein's amino acids
        if residue.id[0] != ' ':
            continue
            
        # Extract the C-alpha (CA) atom coordinates for each residue
        if 'CA' in residue:
            ca_atom = residue['CA']
            residues.append({
                'res_id': residue.id[1],     # The position number (e.g., 98)
                'res_name': residue.resname  # The amino acid name (e.g., PHE)
            })
            coords.append(ca_atom.coord)     # The [X, Y, Z] float coordinates
            
    print(f"Successfully extracted {len(residues)} residues from Chain A.")
    return residues, np.array(coords)

if __name__ == "__main__":
    # Test run to prove it works
    res, coords = parse_pdb()
    print("\n[SUCCESS] Sample of first 3 residues:")
    for i in range(3):
        print(f"Residue {res[i]['res_id']} ({res[i]['res_name']}) -> 3D Coords: {coords[i]}")