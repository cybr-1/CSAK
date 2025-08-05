"""Defangs a given artifact or multiple in a plain text file."""

# import modules
import argparse
import re

# define arguments
parser = argparse.ArgumentParser(description="Defangs a given artifact or multiple in a plain text file.")
parser.add_argument('artifact', nargs='*')
parser.add_argument('-f', '--file', help="Input file containing artifacts",required=False)
parser.add_argument('-o', '--output', help="Output file containing defanged artifacts", required=False )
parser.add_argument('-r', '--replace-file', help="If an input file is declared this will overwrite the artifacts with the defanged values.", required=False, action="store_true")
parser.add_argument('-v', help="Enable verbose output", action="store_true" )
args = parser.parse_args()

# declare global output variable
output_data = []

# declare the regex variables for artifacts
ip_regex = r'((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}'
uri_regex = r'\b[a-zA-Z][a-zA-Z0-9+.-]*:\/\/[^\s/$.?#].[^\s]*'
email_regex = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
domain_regex = r'(?<!@)(?<!:\/\/)(?<!\.)\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b(?!\/)'

# FUNCTION - defang
def defang(text, artifact_type):
    if artifact_type == 'ip':
        defanged = text.replace('.', '[.]')
    elif artifact_type == 'email':
        defanged = text.replace('@', '[@]').replace('.', '[.]')
    elif artifact_type == 'uri':
        if text.startswith('http://'):
            text = text.replace('http://', 'hxxp://', 1)
        elif text.startswith('https://'):
            text = text.replace('https://', 'hxxps://', 1)
        defanged = text.replace('.', '[.]')
    elif artifact_type == 'domain':
        defanged = text.replace('.', '[.]')
    return defanged

# FUNCTION - artifact detection
def detect_artifacts(text):
    cleaned = text.strip()
    if cleaned != "":
        ip_match = re.search(ip_regex, cleaned)
        uri_match = re.search(uri_regex, cleaned)
        email_match = re.search(email_regex, cleaned)
        domain_match = re.search(domain_regex, cleaned)
        if ip_match:
            original = ip_match.group()
            defanged = defang(original, 'ip')
            print(f'[!] Found IP artifact: {original} -> {defanged}')
            output_data.append({
                "type": "IP",
                "original": original,
                "defanged": defanged
            })
        if uri_match:
            original = uri_match.group()
            defanged = defang(original, 'uri')
            print(f'[!] Found URI artifact: {original} -> {defanged}')
            output_data.append({
                "type": "URI",
                "original": original,
                "defanged": defanged
            })
        if email_match:
            original = email_match.group()
            defanged = defang(original, 'email')
            print(f'[!] Found email artifact: {original} -> {defanged}')
            output_data.append({
                "type": "Email",
                "original": original,
                "defanged": defanged
            })
        if domain_match:
            original = domain_match.group()
            defanged = defang(original, 'domain')
            print(f'[!] Found domain artifact: {original} -> {defanged}')
            output_data.append({
                "type": "Domain",
                "original": original,
                "defanged": defanged
            })

# handle the CLI input
if not args.file:
    for art in args.artifact:
        detect_artifacts(art)

# handle the file input
else:
    with open(args.file) as f:
        for line in f.readlines():
            detect_artifacts(line)

# sepcify output
if args.output:
    with open(args.output, 'w') as f:
        for item in output_data:
            f.write(f"Type: {item['type']} | Original: {item['original']} | Defanged: {item['defanged']}\n")


           
                    
                

