import json
from collections import Counter
from typing import Iterable, Union, Dict, Any
from memory.tagger import log_tagged_memory

def load_peer_logs(paths):
    merged = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                merged.extend(f.readlines())
        except Exception:
            continue
    return merged

def _parse_entry(entry: Union[str, Dict[str, Any]], tag: str) -> str:
    """Extract the vote text from a memory entry if it matches the tag."""
    if isinstance(entry, dict):
        if entry.get("topic") != tag:
            return ""
        content = entry.get("content", "")
        if isinstance(content, dict):
            content = str(content)
        return str(content)

    if isinstance(entry, str):
        try:
            data = json.loads(entry)
            return _parse_entry(data, tag)
        except Exception:
            if f"[topic:{tag}]" not in entry:
                return ""
            return entry.split("]")[-1].strip()
    return ""


def swarm_vote(logs: Iterable[Union[str, Dict[str, Any]]], tag: str = "decision") -> Dict[str, int]:
    """Tally yes/no/abstain votes from memory logs."""
    counts = Counter()
    for entry in logs:
        text = _parse_entry(entry, tag).lower()
        if "vote yes" in text:
            counts["yes"] += 1
        elif "vote no" in text:
            counts["no"] += 1
        elif "vote abstain" in text:
            counts["abstain"] += 1

    if not counts:
        return None

    result = {
        "yes": counts.get("yes", 0),
        "no": counts.get("no", 0),
        "abstain": counts.get("abstain", 0),
    }
    result["net"] = result["yes"] - result["no"]

    log_tagged_memory(
        f"Swarm consensus on '{tag}': YES={result['yes']} NO={result['no']} ABSTAIN={result['abstain']} Net={result['net']}",
        topic="swarm",
        trust="high",
    )

    return result
