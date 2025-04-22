def merge_peer_logs(log_paths, output="memory/log.txt"):
    seen = set()
    merged = []
    for path in log_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line not in seen:
                        seen.add(line)
                        merged.append(line)
        except:
            continue
    merged.sort()
    with open(output, "w", encoding="utf-8") as f:
        f.writelines(merged)
    print(f"[🧠] Merged {len(merged)} lines into {output}")
