#!/usr/bin/env python
"""
check_all_domains.py
Run this AFTER run_full_pipeline.py to verify every domain actually
produced valid, current output. Doesn't re-run anything — just checks
what's on disk right now.
"""
import os
import json
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
FRESHNESS_LIMIT_SECONDS = 30 * 60  # flag anything older than 30 min as possibly stale

def check_file_exists(label, path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return False, f"[FAIL] {label}: file not found at {path}"
    return True, full

def check_freshness(label, full_path):
    age = time.time() - os.path.getmtime(full_path)
    if age > FRESHNESS_LIMIT_SECONDS:
        mins = int(age / 60)
        return False, f"[WARN] {label}: file is {mins} min old — may be stale, rerun pipeline before demo"
    return True, f"[OK] {label}: fresh ({int(age)}s old)"

def check_json_valid(label, full_path):
    try:
        with open(full_path, "r") as f:
            data = json.load(f)
        return True, data
    except json.JSONDecodeError as e:
        return False, f"[FAIL] {label}: invalid JSON — {e}"
    except Exception as e:
        return False, f"[FAIL] {label}: could not read — {e}"

def run_all_checks():
    results = []
    all_ok = True

    # --- Domain 2: resistor_output.json ---
    ok, path_or_err = check_file_exists("Domain 2 output", "resistor_output.json")
    if not ok:
        results.append(path_or_err); all_ok = False
    else:
        fresh_ok, fresh_msg = check_freshness("Domain 2 output", path_or_err)
        results.append(fresh_msg)
        json_ok, data_or_err = check_json_valid("Domain 2 output", path_or_err)
        if not json_ok:
            results.append(data_or_err); all_ok = False
        else:
            mutations = data_or_err.get("top_mutations", [])
            if not mutations:
                results.append("[FAIL] Domain 2 output: 'top_mutations' is empty"); all_ok = False
            else:
                required_keys = {"mutation", "position", "binding_delta", "stability_delta", "attribution", "rank"}
                missing = required_keys - set(mutations[0].keys())
                if missing:
                    results.append(f"[FAIL] Domain 2 output: mutation entries missing keys: {missing}"); all_ok = False
                else:
                    results.append(f"[OK] Domain 2 output: {len(mutations)} ranked mutations, all required fields present")

    # --- Domain 3: benchmark_results.json ---
    # NOTE: Path fallback since we might have copied it to the root during the Colab transfer
    bench_path = os.path.join("resistor_gpu", "benchmarks", "benchmark_results.json")
    if not os.path.exists(os.path.join(ROOT, bench_path)):
        bench_path = "benchmark_results.json" # Check root if it's not in the subfolder

    ok, path_or_err = check_file_exists("Domain 3 benchmark", bench_path)
    if not ok:
        results.append(path_or_err); all_ok = False
    else:
        fresh_ok, fresh_msg = check_freshness("Domain 3 benchmark", path_or_err)
        results.append(fresh_msg)
        json_ok, data_or_err = check_json_valid("Domain 3 benchmark", path_or_err)
        if not json_ok:
            results.append(data_or_err); all_ok = False
        else:
            # FIXED SCHEMA CHECK HERE
            if "gpu_seconds" not in data_or_err or "cpu_seconds" not in data_or_err:
                results.append("[FAIL] Domain 3 benchmark: missing 'gpu_seconds' or 'cpu_seconds' key"); all_ok = False
            else:
                gpu_t = data_or_err.get("gpu_seconds")
                cpu_t = data_or_err.get("cpu_seconds")
                speedup = data_or_err.get("speedup_multiplier")
                results.append(f"[OK] Domain 3 benchmark: GPU {gpu_t:.2f}s / CPU {cpu_t:.2f}s / speedup {speedup}x")

    # --- Domain 4: dashboard_payload.json ---
    ok, path_or_err = check_file_exists("Domain 4 report", "dashboard_payload.json")
    if not ok:
        results.append(path_or_err); all_ok = False
    else:
        fresh_ok, fresh_msg = check_freshness("Domain 4 report", path_or_err)
        results.append(fresh_msg)
        json_ok, data_or_err = check_json_valid("Domain 4 report", path_or_err)
        if not json_ok:
            results.append(data_or_err); all_ok = False
        else:
            summary = json.dumps(data_or_err)
            if len(summary) < 100:
                results.append("[FAIL] Domain 4 report: payload looks suspiciously small/empty"); all_ok = False
            else:
                results.append(f"[OK] Domain 4 report: payload present ({len(summary)} chars)")

    # --- Domain 5: frontend data mirror ---
    for fname in ["resistor_output.json", "dashboard_payload.json", "benchmark_results.json"]:
        fpath = os.path.join(ROOT, "frontend", "src", "data", fname)
        if not os.path.exists(fpath):
            results.append(f"[FAIL] Domain 5: frontend/src/data/{fname} not found — did copy step run?"); all_ok = False
        else:
            results.append(f"[OK] Domain 5: frontend/src/data/{fname} present")

    print("\n".join(results))
    print("\n" + ("=" * 50))
    if all_ok:
        print("[SUCCESS] All domains verified. Safe to demo.")
    else:
        print("[ACTION NEEDED] One or more checks failed above — fix before demo.")
    return all_ok

if __name__ == "__main__":
    ok = run_all_checks()
    exit(0 if ok else 1)