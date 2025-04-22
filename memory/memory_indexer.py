def index_memory_by_topic(path="memory/log.txt"):
    from collections import defaultdict
    index = defaultdict(list)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            topic_start = line.find("[topic:")
            if topic_start != -1:
                topic_end = line.find("]", topic_start)
                topic = line[topic_start+7:topic_end]
                index[topic].append(line.strip())
    return index

if __name__ == "__main__":
    idx = index_memory_by_topic()
    for topic, lines in idx.items():
        print(f"\n[🧠 Topic: {topic}]")
        for line in lines[-3:]:
            print(" -", line)
