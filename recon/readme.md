# recon

This directory contains external reconnaissance tools for Aria-node. These are optional, non-core utilities designed to enhance situational awareness using public intelligence feeds and evasive querying strategies.

### Files

- **shodan_scraper.py**
  - Uses Tor to anonymously scrape Shodan web search results.
  - Rotates Tor identity via the Stem library.
  - Extracts IP, port, and organization metadata from results.
  - Outputs targets to `priority_targets.json`.

This tool supports passive recon workflows while avoiding rate limits and detection via Tor routing.
