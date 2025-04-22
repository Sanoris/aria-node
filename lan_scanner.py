import socket
import concurrent.futures
import json
import ipaddress

COMMON_PORTS = [22, 80, 443, 50051]
TIMEOUT = 0.5
OUTPUT = "host_catalog.json"

def scan_ip(ip):
    open_ports = []
    for port in COMMON_PORTS:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            try:
                s.connect((ip, port))
                open_ports.append(port)
            except:
                continue
    return (ip, open_ports) if open_ports else None

def scan_subnet(subnet="192.168.1.0/24"):
    print(f"[🔎] Scanning subnet: {subnet}")
    ips = [str(ip) for ip in ipaddress.IPv4Network(subnet)]
    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        for result in executor.map(scan_ip, ips):
            if result:
                print(f"[✓] Found: {result[0]} open ports: {result[1]}")
                found.append({"ip": result[0], "ports": result[1]})
    with open(OUTPUT, "w") as f:
        json.dump(found, f, indent=2)
    print(f"[💾] Results saved to {OUTPUT}")

if __name__ == "__main__":
    scan_subnet()
