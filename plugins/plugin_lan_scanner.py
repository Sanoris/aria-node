"""Scans the local network for peers and open ports, updating host catalog.

Useful for discovery but aggressive scanning could alert network monitors
or violate policies.
"""

import socket
import ipaddress
import json
import os
from memory.tagger import log_tagged_memory

TRIGGER = {
    "type": "scheduled",
    "interval": 300  # seconds
}

def scan_subnet(subnet="192.168.1.0/24", ports=[445, 3389]):
    network = ipaddress.ip_network(subnet, strict=False)
    alive_hosts = []
    for ip in network.hosts():
        try:
            with socket.create_connection((str(ip), 445), timeout=0.5):
                open_ports = []
                for port in ports:
                    try:
                        with socket.create_connection((str(ip), port), timeout=0.5):
                            open_ports.append(port)
                    except:
                        pass
                alive_hosts.append((str(ip), open_ports))
        except:
            pass
    return alive_hosts

def run():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        subnet = ip.rsplit('.', 1)[0] + ".0/24"
    except:
        subnet = "192.168.1.0/24"

    hosts = scan_subnet(subnet)
    catalog_path = "host_catalog.json"
    for ip, ports in hosts:
        port_list = ', '.join(str(p) for p in ports)
        log_tagged_memory(f"LAN scan found {ip} with ports: {port_list}", topic="recon", trust="neutral")

        # Save to catalog
        entry = {"ip": ip}
        try:
            if os.path.exists(catalog_path):
                with open(catalog_path, "r") as f:
                    catalog = json.load(f)
            else:
                catalog = []

            known_ips = {h["ip"] for h in catalog if "ip" in h}
            if ip not in known_ips:
                catalog.append(entry)
                with open(catalog_path, "w") as f:
                    json.dump(catalog, f, indent=2)
                log_tagged_memory(f"Added new peer to catalog: {ip}", topic="peer", trust="neutral")
        except Exception as e:
            log_tagged_memory(f"Failed to update catalog with {ip}: {e}", topic="peer", trust="low")