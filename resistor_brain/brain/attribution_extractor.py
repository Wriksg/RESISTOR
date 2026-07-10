# Exact mapping of substitutions that yield a score >= 0 in the standard BLOSUM62 matrix.
BLOSUM62_CONSERVATIVE = {
    'A': {'S', 'P', 'T', 'G'},
    'R': {'K', 'Q', 'H'},
    'N': {'D', 'H', 'S'},
    'D': {'N', 'E'},
    'C': set(), # Cysteine is highly unique
    'Q': {'E', 'R', 'K'},
    'E': {'D', 'Q', 'K'},
    'G': {'A', 'S'},
    'H': {'N', 'Y'},
    'I': {'L', 'V', 'M'},
    'L': {'I', 'V', 'M'},
    'K': {'R', 'Q', 'E'},
    'M': {'I', 'L', 'V'},
    'F': {'Y', 'W'},
    'P': {'A'},
    'S': {'T', 'A', 'N'},
    'T': {'S', 'A'},
    'W': {'F', 'Y'},
    'Y': {'F', 'H', 'W'},
    'V': {'I', 'L', 'M'}
}

def get_substitution_severity(wt_aa, mut_aa):
    if wt_aa == mut_aa:
        return "none"
    # Look up real BLOSUM62 evolutionary conservatism
    if mut_aa in BLOSUM62_CONSERVATIVE.get(wt_aa, set()):
        return "conservative"
    return "radical"

def extract_attribution(candidate_dict, wt_seq):
    mut_str = candidate_dict['mutation']
    wt_aa = mut_str[0]
    mut_aa = mut_str[-1]
    pos = candidate_dict['position']
    
    # Context
    pocket_positions = [5, 20, 27, 46, 54, 92, 94, 98]
    context = "binding_pocket" if pos in pocket_positions else "pocket_adjacent"
    
    # Severity
    severity = get_substitution_severity(wt_aa, mut_aa)
    
    # Known Match
    is_known = (mut_str == "F98Y")
    
    candidate_dict['attribution'] = {
        "structural_context": context,
        "substitution_severity": severity,
        "matches_known_resistance": is_known
    }
    return candidate_dict