from memory.tagger import get_recent_memory, log_tagged_memory
from inference.inference_worker import InferenceWorker
import hashlib
from memory.vector_logger import log_vector_record
from trust.endorsement_chain import endorse_peer
from crypto.identity import get_node_id

TRIGGER = {
    "type": "scheduled",
    "interval": 120
}

def handle_result(prompt, output, vector):
    decision = output.lower()
    if "yes" in decision:
        vote = "yes"
    elif "no" in decision:
        vote = "no"
    else:
        vote = "abstain"

    log_tagged_memory(f"VOTE {vote.upper()} — {output}", topic="decision", trust="inferred")

    # optional: fingerprint proposer from prompt if included
    if "Proposing decision:" in prompt:
        try:
            raw = prompt.split("Proposing decision:")[1].split(":")[0]
            proposer = raw.strip()
            if vote == "yes":
                endorser = get_node_id()
                endorse_peer(proposer, endorser, 1.0, f"Auto-voted yes for: {prompt}")
        except Exception as e:
            log_tagged_memory(f"[vote_plugin] Could not parse proposer: {e}", topic="decision", trust="low")

def run():
    memories = get_recent_memory(limit=10)
    for entry in memories:
        content = entry.get("content", "")
        if isinstance(content, dict):
            content = str(content)
        if "Proposing decision:" in content:
            prompt = f"User: {content.strip()}\\nAssistant: Vote yes, no, or abstain with reasoning:"
            InferenceWorker.get().enqueue(prompt, callback=handle_result)
