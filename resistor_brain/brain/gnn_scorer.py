import os
import json
import torch
import sys
from resistor_brain.models.gnn_architecture import ResistorGNN

# --- SYNCED WITH train_gnn.py ---
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

THREE_TO_ONE = {
    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
    'GLU': 'E', 'GLN': 'Q', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
    'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
    'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'
}

class GNNScorer:
    def __init__(self, model_path, graph_path):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.model = ResistorGNN(hidden_dim=64).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        self.model.eval()

        with open(graph_path, 'r') as f:
            graph_data = json.load(f)

        self.nodes = graph_data['nodes']
        self.wt_seq = "".join([THREE_TO_ONE.get(n['name'], n['name']) for n in self.nodes])

        id_to_idx = {node['id']: i for i, node in enumerate(self.nodes)}
        src_edges = [id_to_idx[edge['source']] for edge in graph_data['edges']]
        tgt_edges = [id_to_idx[edge['target']] for edge in graph_data['edges']]
        self.edge_index = torch.tensor([src_edges, tgt_edges], dtype=torch.long).to(self.device)

        base_features = []
        for node in self.nodes:
            # We map node names using the unified dictionary
            aa_idx = AA_TO_IDX.get(node['name'], 0)
            base_features.append([aa_idx, aa_idx])
            
        self.base_features = torch.tensor(base_features, dtype=torch.long).to(self.device)
        self.batch = torch.zeros(self.base_features.size(0), dtype=torch.long).to(self.device)

    def score_mutation(self, node_idx, mutated_aa_code):
        mut_aa_idx = AA_TO_IDX.get(mutated_aa_code, 0)
        x = self.base_features.clone()
        x[node_idx][1] = mut_aa_idx
        mut_idx_tensor = torch.tensor([node_idx], dtype=torch.long).to(self.device)

        with torch.no_grad():
            binding_pred, stability_pred = self.model(x, self.edge_index, self.batch, mut_idx_tensor)
        return binding_pred.item(), stability_pred.item()

    def score_sequence(self, candidate_seq):
        """Adapter method: Diffs candidate against WT, handles multiple mutations!"""
        mutations = []
        for idx, (wt, mut) in enumerate(zip(self.wt_seq, candidate_seq)):
            if wt != mut:
                mutations.append((idx, mut))
        
        if not mutations:
            return 0.0  # WT gets neutral fitness
            
        # [THE FIX]: Accumulate deltas for ALL mutations in the sequence
        total_binding_delta = 0.0
        total_stability_delta = 0.0
        
        for node_idx, mut_aa in mutations:
            b_delta, s_delta = self.score_mutation(node_idx, mut_aa)
            total_binding_delta += b_delta
            total_stability_delta += s_delta
            
        # Negate total binding delta to MAXIMIZE fitness
        base_fitness = -total_binding_delta
        
        # Physics / Plausibility Penalty on the COMBINED stability
        penalty = 0.0
        if total_stability_delta < -1.0:
            penalty = 10.0 + abs(total_stability_delta) # Lethal structure break
        elif total_stability_delta < -0.6:
            penalty = abs(total_stability_delta) * 0.5  # Stressed but survives
            
        # Mild length penalty so it doesn't just mutate the whole protein needlessly
        # (Cost of -0.2 per mutation after the first one)
        complexity_penalty = max(0, len(mutations) - 1) * 0.2
            
        return base_fitness - penalty - complexity_penalty
# Singleton Instance Loader
_scorer_instance = None
def get_scorer():
    global _scorer_instance
    if _scorer_instance is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, '../models/gnn_weights/resistor_gnn_v3.pth')
        graph_path = os.path.join(base_dir, '../../resistor_bio/data/processed/residue_contact_graph.json')
        _scorer_instance = GNNScorer(model_path, graph_path)
    return _scorer_instance