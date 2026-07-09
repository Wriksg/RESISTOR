import os
import json
import torch
import torch.nn.functional as F
from torch.optim import Adam
import random
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(__file__))
from gnn_architecture import ResistorGNN

GRAPH_PATH = os.path.join(BASE_DIR, "resistor_bio", "data", "processed", "residue_contact_graph.json")
CANDIDATES_PATH = os.path.join(BASE_DIR, "resistor_bio", "data", "processed", "candidate_mutations.json")
WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "gnn_weights")

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

# Simulated BLOSUM62 logic: grouped by biochemical properties
def get_substitution_severity(wt, mut):
    if wt == mut:
        return 0.1  # Wild-type (No change = extremely low severity)

    aromatic = {'F', 'W', 'Y'}
    pos_charge = {'R', 'H', 'K'}
    neg_charge = {'D', 'E'}
    aliphatic = {'A', 'I', 'L', 'M', 'V'}
    polar = {'S', 'T', 'N', 'Q'}
    
    groups = [aromatic, pos_charge, neg_charge, aliphatic, polar]
    
    wt_group = next((g for g in groups if wt in g), None)
    mut_group = next((g for g in groups if mut in g), None)

    if wt_group == mut_group:
        return 1.0  # Conservative substitution (e.g., F -> Y)
    elif (wt in pos_charge and mut in neg_charge) or (wt in neg_charge and mut in pos_charge):
        return 3.0  # Radical charge swap
    elif mut == 'P' or mut == 'G':
        return 2.5  # Radical structural break (Proline/Glycine)
    else:
        return 1.5  # Moderate structural change

def train():
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    with open(GRAPH_PATH, 'r') as f: graph_data = json.load(f)
    with open(CANDIDATES_PATH, 'r') as f: candidates = json.load(f)

    # --- DICTIONARY VERIFICATION PRINT ---
    if len(graph_data['nodes']) > 0:
        sample_node_name = graph_data['nodes'][0]['name']
        mapped_idx = AA_TO_IDX.get(sample_node_name, -1)
        print(f"\n[VERIFICATION] Graph Node 'name': {sample_node_name} -> Mapped to AA_TO_IDX: {mapped_idx}")
        if mapped_idx == 0 and sample_node_name not in ['A', 'ALA']:
            print("[WARNING] Mapping failed! Defaulted to 0 (Alanine).")
    
    binding_pocket = [5, 20, 27, 46, 54, 92, 94, 98]
    pocket_neighbors = set()
    for edge in graph_data['edges']:
        if edge['source'] in binding_pocket: pocket_neighbors.add(edge['target'])
        if edge['target'] in binding_pocket: pocket_neighbors.add(edge['source'])

    # --- TOPOLOGY DIAGNOSTIC PRINTS ---
    print("\n--- TOPOLOGY DIAGNOSTICS ---")
    print(f"Is position 1 in binding_pocket? {1 in binding_pocket}")
    print(f"Is position 1 in pocket_neighbors? {1 in pocket_neighbors}")
    print("----------------------------\n")

    # --- BASELINE ANCHORS (NEGATIVE EXAMPLES) ---
    print("[INFO] Injecting Baseline Anchors into training data...")
    id_to_name = {n['id']: n['name'] for n in graph_data['nodes']}
    
    # 1. Inject 150 Harmless Faraway Mutations
    faraway_ids = [n['id'] for n in graph_data['nodes'] if n['id'] not in binding_pocket and n['id'] not in pocket_neighbors]
    for _ in range(150):
        if faraway_ids:
            fid = random.choice(faraway_ids)
            actual_wt = id_to_name.get(fid, 'A')
            candidates.append({'position': fid, 'wild_type': actual_wt, 'mutated': 'A'})
            
    # 2. Inject 50 Wild-Type (No Change) Pocket States
    for pid in binding_pocket:
        actual_wt = id_to_name.get(pid, 'A')
        for _ in range(6):
            candidates.append({'position': pid, 'wild_type': actual_wt, 'mutated': actual_wt})

    pseudo_labels = []
    for c in candidates:
        pos = c['position']
        wt = c['wild_type']
        mut = c['mutated']
        
        severity = get_substitution_severity(wt, mut)

        # Apply severity multiplier to the distance heuristic
        if pos in binding_pocket:
            b_val = (-3.0 * severity) + (random.random() * 0.2)
        elif pos in pocket_neighbors:
            b_val = (-1.5 * severity) + (random.random() * 0.2)
        else:
            b_val = -0.3 + (random.random() * 0.1) # Raised baseline from 0.0 to -0.3
            
        # Stability rules
        if mut == 'P':
            s_val = -3.0
        elif mut == 'G':
            s_val = -2.0
        else:
            s_val = (-0.5 * severity) + (random.random() * -0.2)
        
        pseudo_labels.append((b_val, s_val))

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ResistorGNN(hidden_dim=64).to(device)
    optimizer = Adam(model.parameters(), lr=0.001) 
    
    id_to_idx = {node['id']: i for i, node in enumerate(graph_data['nodes'])}
    edge_src = [id_to_idx[e['source']] for e in graph_data['edges']]
    edge_tgt = [id_to_idx[e['target']] for e in graph_data['edges']]
    edge_index = torch.tensor([edge_src, edge_tgt], dtype=torch.long).to(device)
    batch = torch.zeros(len(graph_data['nodes']), dtype=torch.long).to(device)
    
    # Print label statistics before training
    b_labels = torch.tensor([p[0] for p in pseudo_labels], dtype=torch.float)
    s_labels = torch.tensor([p[1] for p in pseudo_labels], dtype=torch.float)
    print(f"\nBinding Labels -> Min: {b_labels.min():.4f}, Max: {b_labels.max():.4f}, Mean: {b_labels.mean():.4f}, Std: {b_labels.std():.4f}")
    print(f"Stability Labels -> Min: {s_labels.min():.4f}, Max: {s_labels.max():.4f}, Mean: {s_labels.mean():.4f}, Std: {s_labels.std():.4f}")
    
    print("\n--- RESISTOR: GNN Distance + BLOSUM Severity Training ---")
    model.train()
    
    best_loss = float('inf')
    best_weights = None
    
    for epoch in range(1, 101):
        total_loss = 0
        batch_idx = random.sample(range(len(candidates)), 100)
            
        for i in batch_idx:
            optimizer.zero_grad()
            
            # --- THE MEMORY FIX ---
            seq_features = [[AA_TO_IDX.get(n['name'], 0), AA_TO_IDX.get(n['name'], 0)] for n in graph_data['nodes']]
            mut_pos = id_to_idx[candidates[i]['position']]
            seq_features[mut_pos][1] = AA_TO_IDX.get(candidates[i]['mutated'], 0)
            
            x = torch.tensor(seq_features, dtype=torch.long).to(device)
            mut_idx_tensor = torch.tensor([mut_pos], dtype=torch.long).to(device)
            
            bind_pred, stab_pred = model(x, edge_index, batch, mut_idx_tensor)
            
            bind_target = torch.tensor([[pseudo_labels[i][0]]], dtype=torch.float).to(device)
            stab_target = torch.tensor([[pseudo_labels[i][1]]], dtype=torch.float).to(device)
            
            loss = F.mse_loss(bind_pred, bind_target) + F.mse_loss(stab_pred, stab_target)
            loss.backward()
            
            # Optional: Add gradient clipping to prevent wild spikes
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            total_loss += loss.item()
            
        # Track the best model based on total loss
        if total_loss < best_loss:
            best_loss = total_loss
            best_weights = model.state_dict().copy()
            
        if epoch % 20 == 0:
            print(f"Epoch {epoch:03d} | Loss: {total_loss/100:.4f}")
            
    # SAVE AS V3 (Only the best weights)
    save_path = os.path.join(WEIGHTS_DIR, "resistor_gnn_v3.pth")
    torch.save(best_weights, save_path)
    print(f"\n[SUCCESS] Model trained! Best loss achieved: {best_loss/100:.4f}")
    print(f"Best weights saved to {save_path}")

if __name__ == "__main__":
    train()