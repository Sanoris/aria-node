import socket
import ipaddress
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
    # Auto-detect local subnet (placeholder for now)
    ip = socket.gethostbyname(socket.gethostname())
    subnet = ip.rsplit('.', 1)[0] + ".0/24"
    hosts = scan_subnet(subnet)
    for ip, ports in hosts:
        port_list = ', '.join(str(p) for p in ports)
        log_tagged_memory(f"LAN scan found {ip} with ports: {port_list}", topic="recon", trust="neutral")