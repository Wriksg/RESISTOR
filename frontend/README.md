# 🧬 RESISTOR /// Antimicrobial Resistance Prediction Engine

![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TailwindCSS v4](https://img.shields.io/badge/Tailwind_v4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Llama 3.3](https://img.shields.io/badge/Llama_3.3_70B-0466C8?style=for-the-badge)
![AMD ROCm](https://img.shields.io/badge/AMD_ROCm-ED1C24?style=for-the-badge&logo=amd&logoColor=white)

**RESISTOR** is an end-to-end, AI-driven bioinformatics pipeline designed to proactively predict how bacteria will mutate to defeat antibiotics. By simulating evolutionary pathways using structural graph neural networks and genetic algorithms, RESISTOR identifies high-risk resistance mutations *before* they appear in clinical populations.

---

## 🎯 The Milestone: Clinical Validation
During blind validation against *Staphylococcus aureus* Dihydrofolate Reductase (DHFR) targeted by Trimethoprim, the RESISTOR Genetic Algorithm explored an exhaustive search space of ~3,000 mutational pathways. 

**The pipeline successfully recovered `F98Y`—the exact, real-world documented clinical resistance mutation—and flagged it as a critical threat based purely on structural thermodynamics and biochemical heuristics.**

---

## 🏗️ Architecture (The 5 Domains)

RESISTOR is built on a highly decoupled, hardware-agnostic 5-domain architecture:

### 1. Structural Parsing
Parses raw `.pdb` files and drug structures to construct a 3D Alpha-Carbon spatial contact graph, mapping the exact topology of the drug-binding pocket.

### 2. Siamese Graph Neural Network (GNN) & Evolutionary Search
A custom `PyTorch Geometric` GNN evaluates mutations via a dual-channel (Wild-Type vs Mutated) embedding. It scores mutations based on:
- **Binding Disruption (ΔΔG):** Structural proximity to the binding pocket.
- **Protein Stability (ΔΔG):** Evolutionary substitution severity (BLOSUM62 heuristics).
A Genetic Algorithm uses these scores as a fitness function to discover the most dangerous, thermodynamically viable mutations.

### 3. Hardware Telemetry & Benchmarking
The inference pipeline sweeps exhaustive target combinations and benchmarks execution speeds. The architecture is built to be optimized for **AMD ROCm + PyTorch Geometric Batch.from_data_list()** to process thousands of 3D protein graphs in sub-millisecond forward passes.

### 4. LLM Clinical Reasoning Engine
The mathematical outputs of the GNN are piped into a **Llama 3.3 70B** agent via the **Fireworks AI API**. The LLM acts as an automated computational biologist, translating raw thermodynamic deltas into actionable clinical forecast reports. Includes a strict 10-second API timeout guard and cached fallback states for live environment stability.

### 5. Glassmorphic Executive Dashboard
A high-performance **React / Vite / Tailwind v4** frontend. Uses **Zustand** for state management and **Framer Motion** for cinematic UI layout rendering. The dashboard seamlessly hot-reloads when the backend orchestration script injects new JSON telemetry.

---

## 🚀 Running the Pipeline

RESISTOR operates via a master orchestration script that guarantees mathematical synchronization across all 5 domains.

```bash
# 1. Run the entire backend AI pipeline
python run_full_pipeline.py

# 2. Verify all domains are fresh and integrated
python check_all_domains.py

# 3. Start the UI
cd frontend
npm run dev