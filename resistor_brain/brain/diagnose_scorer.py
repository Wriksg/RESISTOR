import sys
import os
# Add project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from resistor_brain.brain.gnn_scorer import get_scorer

def make_mutant(wild_type_seq, mutations):
    """mutations: list of (0-based index, new_aa) tuples"""
    seq_list = list(wild_type_seq)
    for idx, aa in mutations:
        seq_list[idx] = aa
    return "".join(seq_list)


def main():
    scorer = get_scorer()
    wt = scorer.wt_seq

    print("--- RESISTOR: Scorer Diagnostic (bypassing GA) ---")
    print(f"Wild-type sequence length: {len(wt)}\n")

    # Position 98 (1-based) -> index 97; Position 27 (1-based) -> index 26
    F98Y_idx = 97
    D27W_idx = 26

    print(f"Residue at index {F98Y_idx} (expect F for position 98): {wt[F98Y_idx]}")
    print(f"Residue at index {D27W_idx} (expect D for position 27): {wt[D27W_idx]}\n")

    seq_wt = wt
    seq_f98y = make_mutant(wt, [(F98Y_idx, 'Y')])
    seq_d27w = make_mutant(wt, [(D27W_idx, 'W')])
    seq_combo = make_mutant(wt, [(F98Y_idx, 'Y'), (D27W_idx, 'W')])

    cases = [
        ("Wild-Type (no mutation)", seq_wt),
        ("F98Y alone", seq_f98y),
        ("D27W alone", seq_d27w),
        ("F98Y + D27W combined", seq_combo),
    ]

    results = []
    for label, seq in cases:
        fitness = scorer.score_sequence(seq)
        results.append((label, fitness))
        print(f"{label:28s} -> Fitness: {fitness:+.4f}")

    print("\n--- SANITY CHECKS ---")
    wt_fit = results[0][1]
    f98y_fit = results[1][1]
    d27w_fit = results[2][1]
    combo_fit = results[3][1]

    # Check 1: WT should be neutral (0.0 by definition in score_sequence)
    print(f"1. WT fitness is 0.0 (neutral baseline)? {'PASS' if wt_fit == 0.0 else 'FAIL -- ' + str(wt_fit)}")

    # Check 2: single mutants should differ meaningfully from WT and from each other
    single_mutants_distinct = abs(f98y_fit - wt_fit) > 0.1 and abs(d27w_fit - wt_fit) > 0.1
    print(f"2. Single mutants clearly differ from WT? {'PASS' if single_mutants_distinct else 'FAIL -- check for flat/collapsed scoring'}")

    # Check 3: is the combo just literally identical to one of the singles?
    combo_matches_a_single = (abs(combo_fit - f98y_fit) < 1e-6) or (abs(combo_fit - d27w_fit) < 1e-6)
    print(f"3. Combo fitness identical to a single mutant's? {'FAIL -- multi-mutation logic not engaging' if combo_matches_a_single else 'PASS -- combo is genuinely distinct'}")

    # Check 4: does the complexity penalty show up?
    naive_sum = f98y_fit + d27w_fit
    print(f"4. Naive sum of singles: {naive_sum:+.4f} | Actual combo: {combo_fit:+.4f} | Difference: {naive_sum - combo_fit:+.4f}")
    print("   (Difference should be >= ~0.2 due to complexity penalty, more if a stability penalty triggered)")

if __name__ == "__main__":
    main()