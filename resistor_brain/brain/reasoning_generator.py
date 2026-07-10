def generate_reasoning(candidate_dict):
    mut = candidate_dict['mutation']
    attr = candidate_dict['attribution']
    b_delta = candidate_dict['binding_delta']
    s_delta = candidate_dict['stability_delta']
    
    # Base sentence
    context_str = "directly inside the active binding pocket" if attr['structural_context'] == "binding_pocket" else "adjacent to the pocket"
    
    reasoning = f"{mut} is located {context_str}. "
    reasoning += f"This is a {attr['substitution_severity']} substitution that causes a significant predicted disruption to drug binding (Δ {b_delta}) "
    
    # Removed the trailing spaces here
    if s_delta > -0.6:
        reasoning += f"while maintaining excellent protein stability (Δ {s_delta})."
    else:
        reasoning += f"with a moderate cost to protein stability (Δ {s_delta})."
        
    # Moved the space to the front of this string
    if attr['matches_known_resistance']:
        reasoning += " CRITICAL FLAG: This mutation perfectly matches a known, published clinical resistance mutation in S. aureus DHFR."
        
    candidate_dict['reasoning'] = reasoning
    return candidate_dict