#!/usr/bin/env python
"""
run_full_pipeline.py
Runs Domain 2 -> 3 -> 4 in sequence, then copies the two files the
frontend actually reads into frontend/src/data/. Run this ONCE before
any demo/rehearsal so every domain's output is from the same run and
nothing is stale.
"""
import subprocess
import shutil
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DATA = os.path.join(ROOT, "frontend", "src", "data")

STEPS = [
    ("Domain 2: GNN inference + ranking",
     [sys.executable, "-m", "resistor_brain.brain.inference_engine"]),
    ("Domain 3: GPU/CPU benchmark",
     [sys.executable, "resistor_gpu/benchmarks/throughput_logger.py"]),
    ("Domain 4: Fireworks report generation",
     [sys.executable, "-m", "resistor_llm.report_generator"]),
]

FILES_TO_COPY = [
    ("resistor_output.json", "resistor_output.json"),
    ("dashboard_payload.json", "dashboard_payload.json"),
    (os.path.join("resistor_gpu", "benchmarks", "benchmark_results.json"), "benchmark_results.json"),
]

def run_step(name, cmd):
    print(f"\n=== {name} ===")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"[FAIL] {name} exited with code {result.returncode}. Stopping pipeline.")
        sys.exit(1)
    print(f"[OK] {name} complete.")

def main():
    for name, cmd in STEPS:
        run_step(name, cmd)

    os.makedirs(FRONTEND_DATA, exist_ok=True)
    print("\n=== Copying outputs into frontend/src/data ===")
    for src_rel, dst_name in FILES_TO_COPY:
        src = os.path.join(ROOT, src_rel)
        dst = os.path.join(FRONTEND_DATA, dst_name)
        if not os.path.exists(src):
            print(f"[WARNING] {src} not found — skipping. Check the step that should have produced it.")
            continue
        shutil.copy2(src, dst)
        print(f"[OK] {src_rel} -> frontend/src/data/{dst_name}")

    print("\n[SUCCESS] Full pipeline run complete. All frontend data is current.")
    print("Now run: cd frontend && npm run dev")

if __name__ == "__main__":
    main()