"""Monitors ARP traffic to detect new devices and log them in a catalog.

Passively captures network packets, which may reveal device information
without consent.
"""

from scapy.all import sniff, ARP
from memory.tagger import log_tagged_memory
import threading

TRIGGER = {
    "type": "passive"  # Passive listeners run continuously
}
import json
CATALOG = "host_catalog.json"

def add_to_catalog(ip, mac):
    try:
        with open(CATALOG, "r") as f:
            hosts = json.load(f)
    except FileNotFoundError:
        hosts = []

    # Check for duplicates
    for h in hosts:
        if h["ip"] == ip or h.get("mac", None) == mac:
            return False  # Device already exists

    # Add new device
    hosts.append({"ip": ip, "mac": mac, "ports": []})
    with open(CATALOG, "w") as f:
        json.dump(hosts, f, indent=2)
    return True  # New device added

def arp_callback(pkt):
    if ARP in pkt and pkt[ARP].op in (1, 2):
        ip = pkt[ARP].psrc
        mac = pkt[ARP].hwsrc
        if add_to_catalog(ip, mac):
            log_tagged_memory(f"Detected new device: {ip} (MAC: {mac})", topic="recon", trust="neutral")

def run():
    threading.Thread(target=sniff, kwargs={"filter": "arp", "prn": arp_callback, "store": 0}, daemon=True).start()