#!/usr/bin/env python3
"""
ipinfo_lookup.py - Advanced IP information lookup tool
Author: Eyal Zabarsky
Copyright (c) 2025 Eyal Zabarsky
License: MIT

Queries ipinfo.io API for IP address details.
Supports single IP, file input, JSON or CSV output.
Includes retries, IP validation, colors, and verbose logging.
"""

import argparse
import json
import csv
import os
import sys
import time
import ipaddress
import configparser
from pathlib import Path
from typing import List, Dict

import requests
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Default config file path
CONFIG_FILE = Path.home() / ".ipinfo.cfg"

def load_api_token() -> str:
    # Try env var first
    token = os.getenv("IPINFO_TOKEN")
    if token:
        return token
    # Then config file
    if CONFIG_FILE.exists():
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config.get("DEFAULT", "token", fallback="")
    return ""

def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def get_ip_info(ip: str, token: str = "", retries: int = 3, delay: int = 2, verbose: bool = False) -> Dict:
    url = f"https://ipinfo.io/{ip}/json"
    params = {"token": token} if token else {}

    for attempt in range(1, retries + 1):
        try:
            if verbose:
                print(Fore.YELLOW + f"Attempt {attempt}: Querying {ip}...")
            resp = requests.get(url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise Exception(data["error"].get("message", "Unknown API error"))
            return data
        except Exception as e:
            if attempt == retries:
                return {"ip": ip, "error": str(e)}
            if verbose:
                print(Fore.RED + f"Error on attempt {attempt} for {ip}: {e}. Retrying in {delay} seconds...")
            time.sleep(delay * (2 ** (attempt - 1)))  # exponential backoff
    return {"ip": ip, "error": "Failed after retries"}

def print_colored_json(data: Dict):
    json_str = json.dumps(data, indent=2)
    # Basic coloring for keys and errors
    for line in json_str.splitlines():
        line = line.replace('"ip"', Fore.CYAN + '"ip"' + Style.RESET_ALL)
        line = line.replace('"error"', Fore.RED + '"error"' + Style.RESET_ALL)
        print(line)

def save_json(results: List[Dict], filename: str):
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

def save_csv(results: List[Dict], filename: str):
    if not results:
        print(Fore.RED + "No results to save.")
        return
    # Collect all keys to create CSV header
    keys = set()
    for r in results:
        keys.update(r.keys())
    keys = sorted(keys)

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

def parse_args():
    parser = argparse.ArgumentParser(description="Advanced IP info lookup tool using ipinfo.io API")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--ip", help="Single IP address to lookup")
    group.add_argument("-f", "--file", help="File containing list of IP addresses (one per line)")

    parser.add_argument("-o", "--output", help="Output file to save results")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format (default: json)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode (no output except errors)")

    return parser.parse_args()

def main():
    args = parse_args()
    token = load_api_token()
    if not token:
        print(Fore.YELLOW + "Warning: No API token provided. You can set IPINFO_TOKEN env var or ~/.ipinfo.cfg file.")

    # Gather IPs
    ips = []
    if args.ip:
        if not is_valid_ip(args.ip):
            print(Fore.RED + f"Invalid IP address: {args.ip}")
            sys.exit(1)
        ips = [args.ip]
    else:
        try:
            with open(args.file, "r") as f:
                for line in f:
                    ip = line.strip()
                    if ip and is_valid_ip(ip):
                        ips.append(ip)
                    elif ip:
                        print(Fore.RED + f"Skipping invalid IP: {ip}")
        except Exception as e:
            print(Fore.RED + f"Failed to read file: {e}")
            sys.exit(1)

    results = []
    for idx, ip in enumerate(ips, 1):
        if not args.quiet:
            print(Fore.GREEN + f"[{idx}/{len(ips)}] Processing {ip}...")
        data = get_ip_info(ip, token, verbose=args.verbose)
        if not args.quiet:
            print_colored_json(data)
        results.append(data)

    if args.output:
        try:
            if args.format == "json":
                save_json(results, args.output)
            else:
                save_csv(results, args.output)
            print(Fore.GREEN + f"Results saved to {args.output}")
        except Exception as e:
            print(Fore.RED + f"Failed to save output file: {e}")

if __name__ == "__main__":
    main()
