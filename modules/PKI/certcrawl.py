"""Scans all SSL certificates on subdomains of s specified domain and then outputs it into a CSV"""

import requests
import pandas as pd
import argparse


# colour vars
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def fetch_certificates(domain):
    url = f"https://crt.sh/?q={domain}&output=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def process_certificates(certificates):
    df = pd.DataFrame(certificates)
    df['not_before'] = pd.to_datetime(df['not_before'])
    latest_certs = df.sort_values('not_before', ascending=False).drop_duplicates(subset=['name_value'])
    return latest_certs[['name_value', 'common_name', 'not_before', 'not_after']]

def main():
    parser = argparse.ArgumentParser(description="Enumerate all subdomain certificates for a given domain.")
    parser.add_argument("-domain", type=str, help="Enter the domain to enumerate certificates for.", default=None, required=True)
    parser.add_argument("-output", type=str, help="CSV output path, e.g., C:\\tmp\\output.csv", default=None, required=True)
    args = parser.parse_args()
    

    if args.domain is None and args.output is None:
        print("Error: Please specify the domain and output CSV path. See help for usage.")
    elif args.domain is None:
        print("Error: Domain must be specified. See help for usage.")
        return
    elif args.output is None:
        print("Error: Output CSV path must be specified. See help for usage")
        return
    else:
        certificates = fetch_certificates(args.domain)
        latest_certs = process_certificates(certificates)
        latest_certs.to_csv(args.output, index=False)
        print(f"{GREEN}Certificates belonging to subdomains of {args.domain} have successfully exported to the following file: {args.output}{RESET}\n")

if __name__ == "__main__":
    main()
