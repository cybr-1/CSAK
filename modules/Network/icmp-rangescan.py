"""Sends ICMP requests to hosts on a network range to determine which hosts are online"""

import argparse
import ipaddress
import sys
import subprocess
from colorama import Fore, Style, init

init(autoreset=True)

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--range', dest="range", help="Network Range X.X.X.X/X", required=True)
parser.add_argument('-o', '--output', dest="output", help="Output file for live hosts")
parser.add_argument('-v', '--verbose', dest="verbose", help="Verbose output", action='store_true')
args = parser.parse_args()

is_windows = sys.platform.startswith("win")

live_hosts = []


def cidr_to_ips(cidr, strict=False):
    network = ipaddress.ip_network(cidr, strict=strict)
    for ip in network.hosts():
        yield str(ip)


def ping_once(ip: str, wait: int = 1) -> bool | None:
    """Return True if host is up, False if down, None if error"""
    try:
        if is_windows:
            cmd = ["ping", "-n", "1", ip]
        else:
            cmd = ["ping", "-c", "1", "-W", str(wait), ip]
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True if result.returncode == 0 else False

    except subprocess.TimeoutExpired:
        return None
    except OSError:
        return None

try:
    for ip in cidr_to_ips(args.range):
        status = ping_once(ip)
        # Non-verbose: only show up hosts
        if not args.verbose:
            if status is True:
                print(f"{Fore.GREEN}[+] {ip}{Style.RESET_ALL}")
        # Verbose: show all statuses
        else:
            if status is True:
                print(f"{Fore.GREEN}[+] {ip}{Style.RESET_ALL}")
            elif status is False:
                print(f"{Fore.RED}[-] {ip}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[!] {ip}{Style.RESET_ALL}")

        if status is True:
            live_hosts.append(ip)

except ValueError:
    print(f"{Fore.YELLOW}[!] Invalid CIDR range: {args.range}{Style.RESET_ALL}")
    sys.exit(1)

# Optional output file for live hosts
if args.output:
    try:
        with open(args.output, 'w') as f:
            for ip in live_hosts:
                f.write(ip + '\n')
        print(f"{Fore.BLUE}[+] Written {len(live_hosts)} live hosts to {args.output}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[-] Failed to write output file: {e}{Style.RESET_ALL}")
