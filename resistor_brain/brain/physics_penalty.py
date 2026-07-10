def calculate_fitness(binding_delta, stability_delta):
    """
    Calculates the evolutionary fitness of a mutation.
    The Genetic Algorithm wants to MAXIMIZE this number.
    """
    # 1. Base Fitness: We WANT binding_delta to be highly negative (disrupting the drug).
    # So if binding_delta is -1.04, base_fitness becomes +1.04.
    base_fitness = -binding_delta 
    
    # 2. Plausibility / Physics Penalty
    penalty = 0.0
    
    if stability_delta < -1.0:
        # HARSH PENALTY: Protein folds poorly and dies (e.g., LEU5P case)
        penalty = 10.0 + abs(stability_delta)
    elif stability_delta < -0.6:
        # MILD PENALTY: Protein is stressed but survives
        penalty = abs(stability_delta) * 0.5
        
    final_fitness = base_fitness - penalty
    return final_fitness