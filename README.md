# IPInfo Lookup Tool

**ipinfo_lookup.py** is a powerful, easy-to-use command-line tool to fetch detailed IP address information using the [ipinfo.io](https://ipinfo.io/) API.

---

## Features

- Query single IP or bulk IPs from a file
- Supports IPv4 and IPv6 validation
- Outputs results in JSON or CSV format
- Colored terminal output for readability
- Retry with exponential backoff on failures
- Verbose and quiet modes for flexible output
- Configurable API token via environment variable or config file
- Robust error handling

---

## Installation

1. Clone the repo or download the script:
   ```bash
   git clone https://github.com/yourusername/ipinfo_lookup.git
   cd ipinfo_lookup

---

##Usage
Single IP Lookup:
python3 ipinfo_lookup.py -i 8.8.8.8 -v

Bulk Lookup from File:
python3 ipinfo_lookup.py -f ips.txt -o results.json --format json

Save Output as CSV:
python3 ipinfo_lookup.py -f ips.txt -o results.csv --format csv -q

Configuration:
You can provide your ipinfo.io API token in two ways:

Environment variable:
export IPINFO_TOKEN="your_token_here"

Config file ~/.ipinfo.cfg:
[DEFAULT]
token = your_token_here]


License
This project is licensed under the MIT License - see the LICENSE file for details.

Author
Eyal Zabarsky © 2025

References
ipinfo.io API
