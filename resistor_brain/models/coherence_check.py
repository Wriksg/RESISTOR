import os
import json
import torch
from gnn_architecture import ResistorGNN
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GRAPH_PATH = os.path.join(BASE_DIR, "resistor_bio", "data", "processed", "residue_contact_graph.json")
WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "gnn_weights", "resistor_gnn_v2.pth")
AA_MAP = {'ALA': 'A', 'CYS': 'C', 'ASP': 'D', 'GLU': 'E', 'PHE': 'F',
          'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LYS': 'K', 'LEU': 'L',
          'MET': 'M', 'ASN': 'N', 'PRO': 'P', 'GLN': 'Q', 'ARG': 'R',
          'SER': 'S', 'THR': 'T', 'VAL': 'V', 'TRP': 'W', 'TYR': 'Y'}
AA_TO_IDX = {aa: i for i, aa in enumerate("ACDEFGHIKLMNPQRSTVWY")}


def run_check():
    print("\n--- RESISTOR: GNN Coherence Check (mutation-aware) ---")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ResistorGNN(hidden_dim=64).to(device)
    model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=device))
    model.eval()

    with open(GRAPH_PATH, 'r') as f:
        graph_data = json.load(f)

    id_to_idx = {node['id']: i for i, node in enumerate(graph_data['nodes'])}
    edge_src = [id_to_idx[e['source']] for e in graph_data['edges']]
    edge_tgt = [id_to_idx[e['target']] for e in graph_data['edges']]
    edge_index = torch.tensor([edge_src, edge_tgt], dtype=torch.long).to(device)
    batch = torch.zeros(len(graph_data['nodes']), dtype=torch.long).to(device)

    wt_seq = [AA_MAP.get(n['name'], 'A') for n in graph_data['nodes']]

    f98y_seq = wt_seq.copy()
    f98y_mut_idx = id_to_idx[98]
    f98y_seq[f98y_mut_idx] = 'Y'

    t1a_seq = wt_seq.copy()
    t1a_mut_idx = id_to_idx[1]
    t1a_seq[t1a_mut_idx] = 'A'

    def score_seq(seq, mut_idx):
        features = [[AA_TO_IDX.get(aa, 0)] for aa in seq]
        x = torch.tensor(features, dtype=torch.long).to(device)
        mutated_node_idx = torch.tensor([mut_idx], dtype=torch.long).to(device)
        with torch.no_grad():
            b, s = model(x, edge_index, batch, mutated_node_idx)
        return b.item(), s.item()

    print("Evaluating specific biological cases...\n")

    # Wild-type is scored against the SAME node index as F98Y (residue 98),
    # so WT vs F98Y differ ONLY in amino acid identity at that node --
    # this isolates the mutation's effect instead of comparing arbitrary nodes.
    b_wt, s_wt = score_seq(wt_seq, f98y_mut_idx)
    print(f"1. Wild-Type (Baseline)      -> Binding Delta: {b_wt:+.4f} | Stability Delta: {s_wt:+.4f}")

    b_t1a, s_t1a = score_seq(t1a_seq, t1a_mut_idx)
    print(f"2. T1A (Faraway / Harmless)  -> Binding Delta: {b_t1a:+.4f} | Stability Delta: {s_t1a:+.4f}")

    b_f98y, s_f98y = score_seq(f98y_seq, f98y_mut_idx)
    print(f"3. F98Y (Target Resistance)  -> Binding Delta: {b_f98y:+.4f} | Stability Delta: {s_f98y:+.4f}")

    print("\nCONCLUSION:")
    if abs(b_f98y) > abs(b_t1a) and abs(b_f98y - b_wt) > 0.05:
        print("[SUCCESS] The GNN identifies F98Y as higher risk AND distinguishes it from Wild-Type.")
    elif abs(b_f98y - b_wt) <= 0.05:
        print("[WARNING] F98Y is still nearly identical to Wild-Type -- mutation signal still not separating.")
    else:
        print("[WARNING] The GNN thinks the harmless mutation is more dangerous. The pseudo-labels might need tweaking.")
    print("-" * 40)


if __name__ == "__main__":
    run_check()