import os
import json
import numpy as np
from scipy.spatial.distance import pdist, squareform
from pdb_loader import parse_pdb, load_config

# Setup dynamic paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def build_graph():
    # Make sure the 'processed' folder exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    config = load_config()
    cutoff = config.get('distance_cutoff_angstroms', 8.0)
    
    print("\n--- RESISTOR Graph Builder ---")
    residues, coords = parse_pdb()
    
    print(f"Calculating spatial distances (Cutoff: {cutoff}Å)...")
    # pdist and squareform calculate the distance between every pair of 3D points instantly
    dist_matrix = squareform(pdist(coords))
    
    nodes = []
    for res in residues:
        nodes.append({
            "id": res['res_id'],
            "name": res['res_name']
        })
        
    edges = []
    num_residues = len(residues)
    
    # Check every combination of residues
    for i in range(num_residues):
        for j in range(i + 1, num_residues):
            dist = dist_matrix[i, j]
            # If they are close enough in 3D space, draw an edge between them
            if dist <= cutoff:
                edges.append({
                    "source": residues[i]['res_id'],
                    "target": residues[j]['res_id'],
                    "distance": round(float(dist), 3)
                })
                
    # Package it all up for the GNN
    graph_data = {
        "metadata": {
            "target_name": config['target_name'],
            "node_count": len(nodes),
            "edge_count": len(edges),
            "distance_cutoff": cutoff
        },
        "nodes": nodes,
        "edges": edges
    }
    
    # Save the JSON file
    out_path = os.path.join(PROCESSED_DIR, "residue_contact_graph.json")
    with open(out_path, 'w') as f:
        json.dump(graph_data, f, indent=2)
        
    print(f"[SUCCESS] Built graph with {len(nodes)} Nodes and {len(edges)} Edges.")
    print(f"[SUCCESS] Graph saved to: {out_path}\n")

if __name__ == "__main__":
    build_graph()