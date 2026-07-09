import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool

class ResistorGNN(nn.Module):
    def __init__(self, hidden_dim=64):
        super(ResistorGNN, self).__init__()
        
        # Embed 20 amino acids into a dense vector (hidden_dim)
        self.embed = nn.Embedding(20, hidden_dim)

        # Standard message passing layers to understand the 3D structure
        self.conv1 = GCNConv(hidden_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.conv3 = GCNConv(hidden_dim, hidden_dim)

        # Output heads take [Global Structural Context (64) + Isolated Mutation Delta (64)] = 128
        self.bind_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        self.stab_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, x, edge_index, batch, mutated_node_idx):
        # x is shape [N, 2]. 
        # x[:, 0] is the original Wild-Type amino acid
        # x[:, 1] is the current amino acid (which includes the mutation)
        wt_aa = x[:, 0]
        mut_aa = x[:, 1]

        # 1. Embed both sequences independently
        emb_wt_raw = self.embed(wt_aa)
        emb_mut_raw = self.embed(mut_aa)

        # 2. Pass the mutated protein through the GCN to get the smoothed structural context
        h = F.relu(self.conv1(emb_mut_raw, edge_index))
        h = F.relu(self.conv2(h, edge_index))
        h = F.relu(self.conv3(h, edge_index))
        
        # Pool it to get a single vector representing the whole protein pocket's shape
        global_ctx = global_mean_pool(h, batch)

        # 3. Calculate the Biochemical Delta on the RAW embeddings
        # This isolates the exact F -> Y shift BEFORE the graph layers smooth it out
        node_wt_baseline = emb_wt_raw[mutated_node_idx]
        node_mut_baseline = emb_mut_raw[mutated_node_idx]
        biochemical_delta = node_mut_baseline - node_wt_baseline

        # 4. Combine the global structure with the isolated biochemical change
        combined = torch.cat([global_ctx, biochemical_delta], dim=-1)

        # 5. Predict
        bind_pred = self.bind_head(combined)
        stab_pred = self.stab_head(combined)

        return bind_pred, stab_pred