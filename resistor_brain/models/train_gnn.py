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
AA_TO_IDX = {'A': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4, 'G': 5, 'H': 6, 'I': 7,
             'K': 8, 'L': 9, 'M': 10, 'N': 11, 'P': 12, 'Q': 13, 'R': 14,
             'S': 15, 'T': 16, 'V': 17, 'W': 18, 'Y': 19}


def train():
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    with open(GRAPH_PATH, 'r') as f: graph_data = json.load(f)
    with open(CANDIDATES_PATH, 'r') as f: candidates = json.load(f)

    binding_pocket = [5, 20, 27, 46, 54, 92, 94, 98]
    pocket_neighbors = set()
    for edge in graph_data['edges']:
        if edge['source'] in binding_pocket: pocket_neighbors.add(edge['target'])
        if edge['target'] in binding_pocket: pocket_neighbors.add(edge['source'])

    pseudo_labels = []
    for c in candidates:
        pos = c['position']
        if pos in binding_pocket:
            b_val = -3.0 + (random.random() * 0.2)
        elif pos in pocket_neighbors:
            b_val = -1.5 + (random.random() * 0.2)
        else:
            b_val = 0.0 + (random.random() * 0.1)

        s_val = -2.0 if c['mutated'] == 'P' else (random.random() * -0.5)
        pseudo_labels.append((b_val, s_val))

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ResistorGNN(hidden_dim=64).to(device)
    optimizer = Adam(model.parameters(), lr=0.005)

    id_to_idx = {node['id']: i for i, node in enumerate(graph_data['nodes'])}
    edge_src = [id_to_idx[e['source']] for e in graph_data['edges']]
    edge_tgt = [id_to_idx[e['target']] for e in graph_data['edges']]
    edge_index = torch.tensor([edge_src, edge_tgt], dtype=torch.long).to(device)
    batch = torch.zeros(len(graph_data['nodes']), dtype=torch.long).to(device)

    print("\n--- RESISTOR: GNN Distance-Heuristic Training (mutation-aware) ---")
    model.train()

    for epoch in range(1, 51):
        total_loss = 0
        batch_idx = random.sample(range(len(candidates)), 100)

        for i in batch_idx:
            optimizer.zero_grad()
            seq_features = [[AA_TO_IDX.get(n['name'], 0)] for n in graph_data['nodes']]
            mut_pos = id_to_idx[candidates[i]['position']]
            seq_features[mut_pos] = [AA_TO_IDX.get(candidates[i]['mutated'], 0)]

            x = torch.tensor(seq_features, dtype=torch.long).to(device)

            # THE FIX: tell the model which node is mutated so it can pull
            # that node's undiluted embedding after message-passing, instead
            # of relying only on global_mean_pool (which washes out 1/157th
            # of the graph changing).
            mutated_node_idx = torch.tensor([mut_pos], dtype=torch.long).to(device)

            bind_pred, stab_pred = model(x, edge_index, batch, mutated_node_idx)

            bind_target = torch.tensor([[pseudo_labels[i][0]]], dtype=torch.float).to(device)
            stab_target = torch.tensor([[pseudo_labels[i][1]]], dtype=torch.float).to(device)

            loss = F.mse_loss(bind_pred, bind_target) + F.mse_loss(stab_pred, stab_target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if epoch % 10 == 0:
            print(f"Epoch {epoch:02d} | Loss: {total_loss/100:.4f}")

    save_path = os.path.join(WEIGHTS_DIR, "resistor_gnn_v2.pth")
    torch.save(model.state_dict(), save_path)
    print(f"\n[SUCCESS] Model trained using structurally-sound, mutation-aware pooling!")
    print(f"Saved to {save_path} (note: v2 filename since architecture changed)")


if __name__ == "__main__":
    train()