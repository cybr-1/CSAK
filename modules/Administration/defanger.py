"""Defangs a given artifact or multiple in a plain text file."""

import os
import argparse
import re

# define arguments
parser = argparse.ArgumentParser(
    description="Defangs a given artifact or multiple in a plain text file."
)
parser.add_argument('artifact', nargs='*')
parser.add_argument('-f', '--file',help="Input file containing artifacts",required=False)
parser.add_argument('-o', '--output', help="Output file containing defanged artifacts", required=False)
parser.add_argument('-r', '--replace-file',help="If an input file is declared this will overwrite the artifacts with the defanged values.", action="store_true", required=False)
parser.add_argument('-v', '--verbose', help="Enable verbose output", action="store_true")
args = parser.parse_args()

# global list for results
output_data = []

# regex patterns
ip_regex     = r'((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}'
uri_regex    = r'\b[a-zA-Z][a-zA-Z0-9+.-]*:\/\/[^\s/$.?#].[^\s]*'
email_regex  = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
domain_regex = (
    r'(?<!@)(?<!:\/\/)(?<!\.)'  # not email or URI or prefixed by dot
    r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b(?!\/)'
)

# defang function
def defang(text: str, art_type: str) -> str:
    if art_type == 'ip':
        return text.replace('.', '[.]')
    if art_type == 'email':
        return (
            text.replace('@', '[@]').replace('.', '[.]')
        )
    if art_type == 'uri':
        if text.startswith('http://'):
            text = text.replace('http://', 'hxxp://', 1)
        elif text.startswith('https://'):
            text = text.replace('https://', 'hxxps://', 1)
        return text.replace('.', '[.]')
    if art_type == 'domain':
        return text.replace('.', '[.]')
    return text

# artifact detection
def detect_artifacts(line: str):
    text = line.strip()
    if not text:
        return
    for regex, typ in [
        (ip_regex, 'IP'),
        (uri_regex, 'URI'),
        (email_regex, 'Email'),
        (domain_regex, 'Domain')
    ]:
        match = re.search(regex, text)
        if match:
            original = match.group()
            defanged = defang(original, typ.lower())
            print(f"[!] Found {typ} artifact: {original} -> {defanged}")
            output_data.append({
                'type': typ,
                'original': original,
                'defanged': defanged
            })

# process input
if args.file:
    path = os.path.expanduser(args.file)
    with open(path) as f:
        for line in f:
            detect_artifacts(line)
else:
    for art in args.artifact:
        detect_artifacts(art)

# write output file
if args.output:
    outpath = os.path.expanduser(args.output)
    with open(outpath, 'w') as f:
        for item in output_data:
            f.write(
                f"Type: {item['type']} | Original: {item['original']} | Defanged: {item['defanged']}\n"
            )

# optional in-place replace
if args.replace_file and args.file:
    path = os.path.expanduser(args.file)
    with open(path, 'w') as f:
        for item in output_data:
            f.write(item['defanged'] + '\n')
