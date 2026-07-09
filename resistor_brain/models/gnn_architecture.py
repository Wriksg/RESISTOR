
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool


class ResistorGNN(torch.nn.Module):
    def __init__(self, hidden_dim=64):
        super(ResistorGNN, self).__init__()

        self.node_emb = torch.nn.Embedding(num_embeddings=25, embedding_dim=hidden_dim)

        self.conv1 = GCNConv(hidden_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.conv3 = GCNConv(hidden_dim, hidden_dim)

        # Input dim is hidden_dim * 2: pooled graph vector + mutated node's own embedding
        self.binding_head = torch.nn.Linear(hidden_dim * 2, 1)
        self.stability_head = torch.nn.Linear(hidden_dim * 2, 1)

    def forward(self, x, edge_index, batch, mutated_node_idx):
        x = self.node_emb(x.squeeze(-1))

        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.2, training=self.training)

        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.2, training=self.training)

        x = self.conv3(x, edge_index)
        x = F.relu(x)

        graph_vector = global_mean_pool(x, batch)
        mutated_node_vector = x[mutated_node_idx]
        combined = torch.cat([graph_vector, mutated_node_vector], dim=-1)

        binding_delta = self.binding_head(combined)
        stability_delta = self.stability_head(combined)

        return binding_delta, stability_delta


def build_mutated_node_index(batch, local_mutated_indices):
    device = batch.device
    num_graphs = int(batch.max().item()) + 1
    graph_offsets = torch.zeros(num_graphs, dtype=torch.long, device=device)
    for g in range(1, num_graphs):
        graph_offsets[g] = graph_offsets[g - 1] + (batch == (g - 1)).sum()

    local_mutated_indices = torch.as_tensor(local_mutated_indices, dtype=torch.long, device=device)
    return graph_offsets + local_mutated_indices


if __name__ == "__main__":
    print("\n--- RESISTOR: GNN Architecture Test (v2, mutation-aware) ---")

    dummy_x = torch.randint(0, 20, (10, 1))
    dummy_edge_index = torch.tensor([
        [0, 1, 1, 2, 3, 4, 5, 6, 6, 7, 8, 9],
        [1, 0, 2, 1, 4, 3, 6, 5, 7, 6, 9, 8]
    ], dtype=torch.long)
    dummy_batch = torch.tensor([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])

    local_mutated = [2, 4]
    mutated_node_idx = build_mutated_node_index(dummy_batch, local_mutated)
    print(f"Computed global mutated node indices: {mutated_node_idx.tolist()} (expect [2, 9])")

    model = ResistorGNN(hidden_dim=64)
    bind_score, stab_score = model(dummy_x, dummy_edge_index, dummy_batch, mutated_node_idx)

    print(f"Binding Score Shape: {list(bind_score.shape)} -> Expected: [2, 1]")
    print(f"Stability Score Shape: {list(stab_score.shape)} -> Expected: [2, 1]")