import torch
try:
    from torch_geometric.data import Data
    from torch_geometric.nn import GCNConv
    PYG_INSTALLED = True
except ImportError:
    PYG_INSTALLED = False

def check_environment():
    print("\n--- RESISTOR: AMD ROCm + PyG Check ---")
    print(f"PyTorch Version: {torch.__version__}")
    print(f"ROCm/HIP Version: {torch.version.hip}")
    
    # In PyTorch, ROCm/AMD GPUs are still accessed via the 'cuda' alias
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        print(f"[SUCCESS] GPU Detected: {device_name}")
        device = torch.device('cuda')
    else:
        print("[WARNING] No GPU detected by PyTorch. Running on CPU for now.")
        device = torch.device('cpu')
        
    if not PYG_INSTALLED:
        print("[ERROR] PyTorch Geometric is not installed.")
        return
        
    print(f"\nTesting PyTorch Geometric operation on {device.type.upper()}...")
    
    # Create a dummy graph (3 nodes, 2 bidirectional edges, 4 features per node)
    edge_index = torch.tensor([[0, 1, 1, 2],
                               [1, 0, 2, 1]], dtype=torch.long).to(device)
    x = torch.randn(3, 4).to(device)
    data = Data(x=x, edge_index=edge_index)
    
    # Create a tiny 1-layer GNN
    class DummyGNN(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = GCNConv(4, 2)
        def forward(self, data):
            return self.conv(data.x, data.edge_index)
            
    model = DummyGNN().to(device)
    out = model(data)
    
    print(f"[SUCCESS] PyG Message Passing successful! Output shape: {list(out.shape)}\n")

if __name__ == "__main__":
    check_environment()