import os
import json
import torch
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(__file__))
from gnn_architecture import ResistorGNN

GRAPH_PATH = os.path.join(BASE_DIR, "resistor_bio", "data", "processed", "residue_contact_graph.json")
WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "gnn_weights", "resistor_gnn_v3.pth")

# --- BILINGUAL DICTIONARY FIX ---
AA_TO_IDX = {
    'A': 0, 'ALA': 0,
    'C': 1, 'CYS': 1,
    'D': 2, 'ASP': 2,
    'E': 3, 'GLU': 3,
    'F': 4, 'PHE': 4,
    'G': 5, 'GLY': 5,
    'H': 6, 'HIS': 6,
    'I': 7, 'ILE': 7,
    'K': 8, 'LYS': 8,
    'L': 9, 'LEU': 9,
    'M': 10, 'MET': 10,
    'N': 11, 'ASN': 11,
    'P': 12, 'PRO': 12,
    'Q': 13, 'GLN': 13,
    'R': 14, 'ARG': 14,
    'S': 15, 'SER': 15,
    'T': 16, 'THR': 16,
    'V': 17, 'VAL': 17,
    'W': 18, 'TRP': 18,
    'Y': 19, 'TYR': 19
}

def run_check():
    with open(GRAPH_PATH, 'r') as f:
        graph_data = json.load(f)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ResistorGNN(hidden_dim=64).to(device)
    model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=device))
    model.eval()

    id_to_idx = {node['id']: i for i, node in enumerate(graph_data['nodes'])}
    edge_src = [id_to_idx[e['source']] for e in graph_data['edges']]
    edge_tgt = [id_to_idx[e['target']] for e in graph_data['edges']]
    edge_index = torch.tensor([edge_src, edge_tgt], dtype=torch.long).to(device)
    batch = torch.zeros(len(graph_data['nodes']), dtype=torch.long).to(device)

    def evaluate_mutation(target_pos, mut_aa_name):
        seq_features = [[AA_TO_IDX.get(n['name'], 0), AA_TO_IDX.get(n['name'], 0)] for n in graph_data['nodes']]
        
        if target_pos in id_to_idx:
            mut_pos = id_to_idx[target_pos]
            seq_features[mut_pos][1] = AA_TO_IDX.get(mut_aa_name, 0)
        else:
            mut_pos = 0 
            
        x = torch.tensor(seq_features, dtype=torch.long).to(device)
        mut_idx_tensor = torch.tensor([mut_pos], dtype=torch.long).to(device)

        print(f"  Target pos: {target_pos}, Mutation: {mut_aa_name}")
        print(f"  mut_pos index: {mut_pos}, seq_features[mut_pos]: {seq_features[mut_pos]}")
        print(f"  mut_idx_tensor: {mut_idx_tensor.item()}")

        with torch.no_grad():
            bind, stab = model(x, edge_index, batch, mut_idx_tensor)
        return bind.item(), stab.item()

    print("\n--- RESISTOR: GNN Coherence Check (Siamese Architecture) ---")
    print("Evaluating specific biological cases...\n")

    pocket = [5, 20, 27, 46, 54, 92, 94, 98]

    # 1. Wild-Type
    wt_node = next(n for n in graph_data['nodes'] if n['id'] == 98)
    b_wt, s_wt = evaluate_mutation(98, wt_node['name'])
    print(f"1. Wild-Type (Baseline)      -> Binding Delta: {b_wt:+.4f} | Stability Delta: {s_wt:+.4f}\n")

    # 2. Faraway / Harmless
    try:
        far_node = next(n for n in graph_data['nodes'] if n['id'] not in pocket)
        b_far, s_far = evaluate_mutation(far_node['id'], 'A') 
        print(f"2. {far_node['name']}{far_node['id']}A (Faraway / Harmless)  -> Binding Delta: {b_far:+.4f} | Stability Delta: {s_far:+.4f}\n")
    except StopIteration:
        print("2. Faraway / Harmless        -> [Skipped]\n")

    # 3. F98Y (Target Resistance)
    b_f98y, s_f98y = evaluate_mutation(98, 'Y')
    print(f"3. F98Y (Target Resistance)  -> Binding Delta: {b_f98y:+.4f} | Stability Delta: {s_f98y:+.4f}\n")

    # 4. Alt Pocket Generalization
    try:
        alt_node = next(n for n in graph_data['nodes'] if n['id'] in pocket and n['id'] != 98)
        alt_mut = 'P' if alt_node['name'] not in ['PRO', 'P'] else 'W'
        b_alt, s_alt = evaluate_mutation(alt_node['id'], alt_mut)
        print(f"4. {alt_node['name']}{alt_node['id']}{alt_mut} (Alt Pocket Gen) -> Binding Delta: {b_alt:+.4f} | Stability Delta: {s_alt:+.4f}\n")
    except StopIteration:
        print("4. Alt Pocket Gen           -> [Skipped]\n")

if __name__ == "__main__":
    run_check()