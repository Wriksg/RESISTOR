import random
from typing import List, Dict

# Import your newly cleaned GA loop and dummy scorer
from ga_loop import GeneticAlgorithm, dummy_fitness_scorer, DummyConfig
class PSOOptimizer:
    def __init__(self, config, target_positions: List[int], wild_type: str = None):
        """
        Swarm-GA Hybrid Optimizer with a Parallel Epistatic (Outer World) Reservoir
        and local stagnation-triggered quantum-inspired tunneling crossovers.
        """
        self.config = config
        self.target_positions = target_positions
        self.wild_type = wild_type

        self.ga_engine = GeneticAlgorithm(config, target_positions)

        self.global_best_seq = None
        self.global_best_score = -float('inf')
        self.generations_completed = 0

        # High-performance cache to avoid redundant evaluations
        self.score_cache = {}

        # --- PARALLEL EPISTATIC RESERVOIR (OUTER WORLD BUFFER) ---
        self.outer_world_reservoir: List[Dict] = []
        self.reservoir_size = getattr(config, "reservoir_size", 4)

    def _update_outer_world_reservoir(self, sequence: str, score: float):
        if not self.wild_type:
            return

        mutated_positions = {
            pos for pos in self.target_positions
            if pos < len(sequence) and pos < len(self.wild_type) and sequence[pos] != self.wild_type[pos]
        }
        if not mutated_positions:
            return

        for candidate in self.outer_world_reservoir:
            if candidate["mutated_positions"] == mutated_positions:
                if score > candidate["score"]:
                    candidate["sequence"] = sequence
                    candidate["score"] = score
                return

        if len(self.outer_world_reservoir) < self.reservoir_size:
            self.outer_world_reservoir.append({
                "sequence": sequence,
                "score": score,
                "mutated_positions": mutated_positions
            })
            print(f" [Outer World] Preserved epistatic seed {sequence[:10]}... (Score: {score:.4f})")
        else:
            self.outer_world_reservoir.sort(key=lambda x: x["score"])
            if score > self.outer_world_reservoir[0]["score"]:
                self.outer_world_reservoir[0] = {
                    "sequence": sequence,
                    "score": score,
                    "mutated_positions": mutated_positions
                }

    def _score(self, sequence: str) -> float:
        """Calculates fitness, using the dummy scorer for Part 3."""
        if sequence in self.score_cache:
            return self.score_cache[sequence]

        # Use the dummy scorer from ga_loop.py
        final_score = dummy_fitness_scorer(sequence)

        self.score_cache[sequence] = final_score
        return final_score

    def optimize(self, wild_type: str) -> List[Dict]:
        print(f"\nInitializing swarm of {self.config.swarm_size} particles with Outer World Reservoir...")

        if wild_type and not self.wild_type:
            self.wild_type = wild_type

        initial_population = self.ga_engine.initialize_population(wild_type)
        swarm_seqs = initial_population[:self.config.swarm_size]

        particles = []
        for seq in swarm_seqs:
            score = self._score(seq)
            particles.append({
                "current": seq,
                "pbest": seq,
                "pbest_score": score,
                "stagnation_count": 0
            })
            if score > self.global_best_score:
                self.global_best_score = score
                self.global_best_seq = seq

        generations_without_improvement = 0

        for gen in range(self.config.generations):
            improvement_this_gen = False

            for i, particle in enumerate(particles):
                r = random.random()
                candidate = None
                tunneling_occurred = False

                particle_patience = getattr(self.config, "particle_patience", 3)
                if particle.get("stagnation_count", 0) >= particle_patience:
                    if len(self.outer_world_reservoir) >= 2:
                        seeds = random.sample(self.outer_world_reservoir, 2)
                        candidate = self.ga_engine.crossover(seeds[0]["sequence"], seeds[1]["sequence"])
                        tunneling_occurred = True
                    elif self.outer_world_reservoir:
                        seed = random.choice(self.outer_world_reservoir)
                        crossed = self.ga_engine.crossover(particle["current"], seed["sequence"])
                        candidate = self.ga_engine.mutate(crossed, force=True)
                        tunneling_occurred = True

                if not candidate:
                    if r < 0.33 and self.global_best_seq:
                        candidate = self.ga_engine.crossover(particle["current"], self.global_best_seq)
                        candidate = self.ga_engine.mutate(candidate, force=True)
                    elif r < 0.66:
                        candidate = self.ga_engine.mutate(particle["pbest"], force=True)
                    else:
                        candidate = self.ga_engine.mutate(self.wild_type, force=True)

                new_score = self._score(candidate)

                if new_score < self.global_best_score:
                    self._update_outer_world_reservoir(candidate, new_score)

                if new_score > particle["pbest_score"]:
                    particle["current"] = candidate
                    particle["pbest"] = candidate
                    particle["pbest_score"] = new_score
                    particle["stagnation_count"] = 0
                    improvement_this_gen = True

                    if new_score > self.global_best_score:
                        self.global_best_score = new_score
                        self.global_best_seq = candidate
                else:
                    particle["stagnation_count"] = particle.get("stagnation_count", 0) + 1

            if improvement_this_gen:
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1

            self.generations_completed = gen + 1

            if generations_without_improvement >= self.config.patience:
                print(f"Converged at generation {gen + 1}. Early stopping triggered.")
                break

            print(f"Generation {gen + 1}/{self.config.generations} | Best Score: {self.global_best_score:.4f}")

        seen = set()
        final_swarm = []

        for p in particles:
            if p["pbest"] not in seen:
                seen.add(p["pbest"])
                final_swarm.append({"sequence": p["pbest"], "score": p["pbest_score"]})

        final_swarm.sort(key=lambda x: x["score"], reverse=True)
        return final_swarm

if __name__ == "__main__":
    print("\n--- RESISTOR: PSO Optimizer (AETHER Port) ---")
    
    # Create an extended Dummy Config to support PSO requirements
    class PSODummyConfig(DummyConfig):
        def __init__(self):
            super().__init__()
            self.swarm_size = 10
            self.generations = 15
            self.patience = 5
            self.reservoir_size = 4
            self.particle_patience = 3

    config = PSODummyConfig()
    target_positions = [5, 20, 27, 46, 54, 92, 94, 98]
    wild_type_seq = "A" * 157
    
    optimizer = PSOOptimizer(config, target_positions)
    results = optimizer.optimize(wild_type_seq)
    
    print("\n[SUCCESS] PSO Optimization Complete!")
    print(f"Top Candidate Score: {results[0]['score']:.4f}")