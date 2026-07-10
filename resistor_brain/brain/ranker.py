def seq_to_mutations(wt_seq, mut_seq):
    muts = []
    for idx, (wt, mut) in enumerate(zip(wt_seq, mut_seq)):
        if wt != mut:
            muts.append(f"{wt}{idx+1}{mut}")
    return " + ".join(muts) if muts else "WT"

def rank_candidates(all_seen_candidates, wt_seq, scorer, top_n=10):
    analyzed_candidates = []
    
    for seq in all_seen_candidates:
        mut_str = seq_to_mutations(wt_seq, seq)
        
        # Keep it to single-point mutations for clean reporting
        if mut_str == "WT" or "+" in mut_str:
            continue 
            
        for i, (w, m) in enumerate(zip(wt_seq, seq)):
            if w != m:
                b_delta, s_delta = scorer.score_mutation(i, m)
                analyzed_candidates.append({
                    'mutation': mut_str,
                    'position': i + 1,
                    'binding_delta': round(b_delta, 4),
                    'stability_delta': round(s_delta, 4)
                })
                break

    # Pareto Filter: Must disrupt binding
    viable = [c for c in analyzed_candidates if c['binding_delta'] < -0.80]
    
    # Sort by Stability
    ranked = sorted(viable, key=lambda x: x['stability_delta'], reverse=True)
    
    return ranked[:top_n]