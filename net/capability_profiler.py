import re
from collections import Counter

def analyze_skills(log_path="memory/log.txt"):
    pattern = re.compile(r"plugin ([a-zA-Z0-9_]+)")
    skills = Counter()
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            matches = pattern.findall(line)
            for m in matches:
                skills[m] += 1
    return dict(skills)

if __name__ == "__main__":
    skills = analyze_skills()
    for k, v in skills.items():
        print(f"{k}: {v}")
