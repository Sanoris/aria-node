import os
import ast
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_DIR = os.path.join(SCRIPT_DIR, "..", "plugins")
DOCS_DIR = os.path.join(SCRIPT_DIR, "..", "docs")
DOC_OUT_MD = os.path.join(DOCS_DIR, "plugins.md")
DOC_OUT_JSON = os.path.join(DOCS_DIR, "plugins.json")
os.makedirs(DOCS_DIR, exist_ok=True)

def extract_fallback_docstring(source):
    """Grabs leading comment block if no real docstring is found."""
    lines = source.splitlines()
    comment_lines = []
    for line in lines:
        if line.strip().startswith("#"):
            comment_lines.append(line.strip("# ").strip())
        elif line.strip() == "":
            continue
        else:
            break  # Stop at first non-comment, non-empty line
    return "\n".join(comment_lines) if comment_lines else "*No docstring provided.*"

def extract_docstring_and_trigger(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
        docstring = ast.get_docstring(tree)
    except SyntaxError as e:
        return f"*Failed to parse file: {e}*", None

    if not docstring:
        docstring = extract_fallback_docstring(source)

    trigger_dict = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TRIGGER":
                    try:
                        trigger_dict = ast.literal_eval(node.value)
                    except Exception:
                        trigger_dict = "*Could not parse TRIGGER.*"

    return docstring.strip(), trigger_dict

# Collect structured plugin data
plugin_index = []

with open(DOC_OUT_MD, "w", encoding="utf-8") as out:
    out.write("# Plugin Documentation\n\n")

    for filename in sorted(os.listdir(PLUGIN_DIR)):
        if filename.startswith("plugin_") and filename.endswith(".py"):
            filepath = os.path.join(PLUGIN_DIR, filename)
            out.write(f"## `{filename}`\n\n")

            doc, trigger = extract_docstring_and_trigger(filepath)
            out.write(doc + "\n\n")

            plugin_entry = {
                "name": filename,
                "description": doc,
                "trigger": trigger,
            }

            if trigger:
                out.write("**Trigger:**\n")
                out.write("```json\n")
                try:
                    out.write(json.dumps(trigger, indent=2) + "\n")
                except Exception:
                    out.write(str(trigger) + "\n")
                out.write("```\n\n")

            out.write("---\n\n")
            plugin_index.append(plugin_entry)

# Write JSON index
with open(DOC_OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(plugin_index, f, indent=2)

print(f"[✓] Plugin docs generated at: {DOC_OUT_MD}")
print(f"[✓] Plugin index saved at: {DOC_OUT_JSON}")
