# plugin_genetic_evolver.py
import random
import importlib.util
import os
import shutil

PLUGIN_DIR = "plugins"
GENERATIONS = 10
POPULATION_SIZE = 5
MUTATION_RATE = 0.2

def list_plugins():
    return [f for f in os.listdir(PLUGIN_DIR) if f.startswith("plugin_") and f.endswith(".py")]

def load_plugin_code(filename):
    with open(os.path.join(PLUGIN_DIR, filename), "r") as f:
        return f.read()

def mutate_code(code):
    lines = code.split("\n")
    if lines and random.random() < MUTATION_RATE:
        i = random.randint(0, len(lines) - 1)
        lines[i] = "# Mutated: " + lines[i]
    return "\n".join(lines)

def crossover_code(code1, code2):
    lines1 = code1.split("\n")
    lines2 = code2.split("\n")
    cut = random.randint(1, min(len(lines1), len(lines2)) - 1)
    return "\n".join(lines1[:cut] + lines2[cut:])

def evaluate_fitness(filename):
    # Placeholder: fitness = file length (stand-in for real-world performance metrics)
    return len(load_plugin_code(filename))

def evolve_plugins():
    plugins = list_plugins()
    if len(plugins) < 2:
        print("Not enough plugins to evolve.")
        return

    for generation in range(GENERATIONS):
        print(f"Generation {generation+1}")

        population = random.sample(plugins, min(POPULATION_SIZE, len(plugins)))
        fitness_scores = [(plugin, evaluate_fitness(plugin)) for plugin in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)

        parent1, parent2 = fitness_scores[0][0], fitness_scores[1][0]
        code1 = load_plugin_code(parent1)
        code2 = load_plugin_code(parent2)

        new_code = crossover_code(code1, code2)
        new_code = mutate_code(new_code)

        new_plugin_name = f"plugin_evolved_{generation+1}.py"
        with open(os.path.join(PLUGIN_DIR, new_plugin_name), "w") as f:
            f.write(new_code)
        print(f"Created {new_plugin_name}")

if __name__ == "__main__":
    evolve_plugins()