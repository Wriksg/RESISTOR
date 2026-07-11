def build_report_prompt(target_name, top_mutations):
    """
    Constructs a highly constrained prompt using our exact GNN outputs.
    """
    prompt = f"Target Protein: {target_name}\n\n"
    prompt += "Our Graph Neural Network (GNN) has identified the following top resistance mutations based on binding disruption and structural stability:\n\n"
    
    for mut in top_mutations[:3]: # We only send the top 3 to keep the prompt focused
        prompt += f"- Mutation: {mut['mutation']} (Rank {mut['rank']})\n"
        prompt += f"  Binding Delta: {mut['binding_delta']} (More negative = higher disruption to drug)\n"
        prompt += f"  Stability Delta: {mut['stability_delta']} (Must be > -1.0 to survive)\n"
        prompt += f"  Context: {mut['attribution']['structural_context']}, Severity: {mut['attribution']['substitution_severity']}\n"
        if mut['attribution']['matches_known_resistance']:
            prompt += "  *CRITICAL*: Matches known clinical resistance literature.\n"
        prompt += "\n"
        
    prompt += """
Based ONLY on the data above, write a brief, professional Executive Forecast Report (max 3 paragraphs). 
1. Acknowledge the known clinical threat if one exists.
2. Highlight the most dangerous novel threat based on the binding/stability trade-off.
3. Keep the tone clinical, objective, and suited for a pharmaceutical dashboard.
Do not use markdown formatting like **bold** or *italics*.
"""
    return prompt