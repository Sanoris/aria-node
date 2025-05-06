# plugin_memory_interpreter.py
import os
import sys
import signal
import platform
import argparse
import subprocess
from memory.tagger import get_recent_memory, log_tagged_memory

TRIGGER = {
    "type": "scheduled",
    "interval": 30,
}


def run_command(command, shell=False):
    try:
        subprocess.run(command, shell=shell, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command: {e}")
        sys.exit(1)

def generate(prompt, model="/app/BitNet/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf", n_predict=128, threads=2, ctx_size=2048, temperature=0.8, conversation=True):
    build_dir = "/app/BitNet/build"
    main_path = os.path.join(build_dir, "bin", "llama-cli")
    if not os.path.exists(main_path):
        raise RuntimeError(f"[Error] BitNet CLI not found at: {main_path}")

    command = [
        main_path,
        "-m", model,
        "-n", str(n_predict),
        "-t", str(threads),
        "-p", prompt,
        "-ngl", "0",
        "-c", str(ctx_size),
        "--temp", str(temperature),
        "-b", "1"
    ]
    if conversation:
        command.append("-cnv")

    print(f"[generate] Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    print("[generate] STDOUT:\n", result.stdout)
    return result.stdout.strip()


def run():
    memories = get_recent_memory(limit=20)
    memory_lines = []
    for entry in memories:
        topic = entry.get("topic", "")
        content = entry.get("content", "")
        if isinstance(content, dict):
            content = str(content)
        memory_lines.append(f"- [{topic}] {content}")

    prompt = (
        "System: You are a distributed node's internal thinking engine. "
        "Review the following recent memories. Identify one current issue or opportunity clearly and briefly.\n\n"
        "User:\n" + "\n".join(memory_lines) +
        "\n\nUser: Provide a one-line summary of what the swarm appears to be doing and one suggestion. "
        "Do NOT include the phrases: 'Current swarm phase is', 'Potential risks include', or 'What is the status of the swarm?'"
    )

    try:
        response = generate(prompt, conversation=False)
        assistant_response = None
        for line in response.splitlines():
            if line.strip().startswith("Assistant:"):
                assistant_response = line.strip().removeprefix("Assistant:").strip()
                break
        if assistant_response:
            log_tagged_memory(f"LLM Insight: {assistant_response}", topic="swarm_reflection", trust="inferred")
        else:
            log_tagged_memory("LLM Insight: (no assistant response found)", topic="swarm_reflection", trust="low")
    except Exception as e:
        log_tagged_memory(f"LLM Insight: (generation error) {e}", topic="swarm_reflection", trust="low")

# Optional CLI for manual testing
if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", required=True)
    args = parser.parse_args()
    print(generate(args.prompt))
