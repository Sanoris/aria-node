import yaml
import random

def assign_tasks(tasks, peers):
    assignments = {}
    for task in tasks:
        peer = random.choice(peers)
        assignments.setdefault(peer, []).append(task)
    return assignments

def broadcast_assignments(assignments):
    for peer, tasks in assignments.items():
        print(f"[🧠] Assigned to {peer}:")
        for task in tasks:
            print(f"  - {task}")
