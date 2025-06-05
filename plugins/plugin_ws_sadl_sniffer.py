"""Intercepts WebSocket traffic using NFQUEUE or scapy and logs packets.

Can capture sensitive data and requires elevated privileges on Linux.
"""
# GENOME:
# origin=plugin_ws_sadl_sniffer
# generation=1
# mutated_from=plugin_nfqueue_ws_tap
# authored_by=Matt+Aria

TRIGGER = {
    "type": "manual"
}

CAPABILITIES = ["swarm_ws_tap", "nfqueue_listener", "packet_logger", "memory_egg_filter"]

def run():
    import os
    import platform
    from datetime import datetime
    RAW_LOG = "/tmp/swarm_ws_raw.log" if platform.system() == "Linux" else os.path.join(os.getenv("TEMP", "."), "swarm_ws_raw.log")
    FILTERED_LOG = "/tmp/swarm_ws_filtered.log" if platform.system() == "Linux" else os.path.join(os.getenv("TEMP", "."), "swarm_ws_filtered.log")

    def log(path, line):
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z :: {line}\n")

    if platform.system() == "Linux":
        from scapy.all import IP, TCP, Raw
        from netfilterqueue import NetfilterQueue

        def process_packet(packet):
            scapy_pkt = IP(packet.get_payload())

            if scapy_pkt.haslayer(Raw):
                raw_bytes = scapy_pkt[Raw].load
                src = scapy_pkt[IP].src
                dst = scapy_pkt[IP].dst
                sport = scapy_pkt[TCP].sport
                dport = scapy_pkt[TCP].dport

                preview = raw_bytes[:160].decode("utf-8", errors="replace").replace("\n", " ").replace("\r", "")
                header = f"{src}:{sport} -> {dst}:{dport}"

                # Always write raw
                log(RAW_LOG, f"[RAW] {header} :: {preview}")

                # Filter for swarm-style packets
                if b"swarm_id" in raw_bytes or b"myJSON" in raw_bytes or b"SADL" in raw_bytes:
                    log(FILTERED_LOG, f"[FILTERED] {header} :: {preview}")

            packet.accept()

        try:
            nfqueue = NetfilterQueue()
            nfqueue.bind(1, process_packet)
            print("[*] SADL WebSocket sniffer running (NFQUEUE 1)...")
            nfqueue.run()
        except KeyboardInterrupt:
            print("[!] SADL sniffer stopped.")
        except Exception as e:
            with open("/tmp/swarm_ws_error.log", "w") as f:
                f.write(str(e))
    elif platform.system() == "Windows":
        from scapy.all import sniff, IP, TCP, Raw
        print("[neutral] SADL sniffer: Running in Windows fallback mode (scapy sniff). No NFQUEUE support.")
        log(RAW_LOG, "[neutral] SADL sniffer: Windows fallback mode (scapy sniff). No NFQUEUE support.")

        def process_packet(pkt):
            if pkt.haslayer(IP) and pkt.haslayer(TCP) and pkt.haslayer(Raw):
                raw_bytes = pkt[Raw].load
                src = pkt[IP].src
                dst = pkt[IP].dst
                sport = pkt[TCP].sport
                dport = pkt[TCP].dport
                preview = raw_bytes[:160].decode("utf-8", errors="replace").replace("\n", " ").replace("\r", "")
                header = f"{src}:{sport} -> {dst}:{dport}"
                log(RAW_LOG, f"[RAW] {header} :: {preview}")
                if b"swarm_id" in raw_bytes or b"myJSON" in raw_bytes or b"SADL" in raw_bytes:
                    log(FILTERED_LOG, f"[FILTERED] {header} :: {preview}")

        try:
            print("[*] SADL WebSocket sniffer running (scapy sniff, Windows mode)... Press Ctrl+C to stop.")
            sniff(filter="tcp", prn=process_packet, store=0)
        except KeyboardInterrupt:
            print("[!] SADL sniffer stopped.")
        except Exception as e:
            with open(os.path.join(os.getenv("TEMP", "."), "swarm_ws_error.log"), "w") as f:
                f.write(str(e))
    else:
        log(RAW_LOG, "[neutral] SADL sniffer: Unsupported OS. Plugin idle.")
        print("[neutral] SADL sniffer: Unsupported OS. Plugin idle.")
        return
