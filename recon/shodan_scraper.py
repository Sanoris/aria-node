
import requests
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
import time
import json

TOR_PROXY = "socks5h://127.0.0.1:9050"
SEARCH_URL = "https://www.shodan.io/search?query=port%3A22+country%3AUS"
OUTPUT_FILE = "priority_targets.json"

def new_tor_identity():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            print("[+] TOR identity rotated.")
    except Exception as e:
        print(f"[!] Tor identity rotation failed: {e}")

def get_shodan_results():
    proxies = {
        "http": TOR_PROXY,
        "https": TOR_PROXY
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AriaReconBot/1.0)"
    }

    print("[*] Fetching Shodan HTML over Tor...")
    try:
        resp = requests.get(SEARCH_URL, proxies=proxies, headers=headers, timeout=30)
        if "captcha" in resp.text.lower():
            print("[!] CAPTCHA detected — need new Tor identity")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        results = []

        for result in soup.select(".search-result"):
            ip = result.select_one(".ip").text.strip()
            port = result.select_one(".port").text.strip() if result.select_one(".port") else "?"
            org = result.select_one(".org").text.strip() if result.select_one(".org") else "Unknown"
            results.append({
                "ip": ip,
                "port": port,
                "org": org
            })

        print(f"[+] Found {len(results)} IPs.")
        return results

    except Exception as e:
        print(f"[!] Failed to fetch: {e}")
        return []

if __name__ == "__main__":
    while True:
        targets = get_shodan_results()
        if targets:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(targets, f, indent=2)
        new_tor_identity()
        time.sleep(300)  # Wait 5 min between batches
