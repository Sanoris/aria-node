import yaml
from memory.memcore import log_memory, load_personality
from brain.aria_core import AriaBrain

with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

brain = AriaBrain(cfg["model"])
persona = load_personality(cfg["personality_file"])

print(f"[+] {cfg['node_name']} booted.")
print("Aria is awake.\n")

while True:
    try:
        user = input("You: ")
        prompt = f"{persona}\n\nUser: {user}\nAria:"
        reply = brain.respond(prompt)
        print("Aria:", reply)
        log_memory(user, reply)
    except KeyboardInterrupt:
        print("\n[!] Node shutdown requested.")
        break