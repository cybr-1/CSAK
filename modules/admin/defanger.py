"""Defangs a given artifact or multiple in a plain text file."""

# import modules
import argparse
import re

# define arguments
parser = argparse.ArgumentParser(description="Defangs a given artifact or multiple in a plain text file.")
parser.add_argument('artifact', nargs='+')
parser.add_argument('-f', '--file',required=False, action="store_true")
args = parser.parse_args()

# declare the regex variables for artifacts
ip_regex = r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$'

# handle the CLI input
if not args.file:
    artifact = args.artifact
    for art in artifact:
        print(f'[*] Recieved artifact: {art}')

# handle the file input
else:
    with open(args.artifact[0]) as f:
        for line in f.readlines():
            cleaned = line.strip()
            if cleaned != "":
                ip_match = re.search(ip_regex, cleaned)
                if ip_match:
                    print(f'[!] Found IP artifact: {cleaned}')

