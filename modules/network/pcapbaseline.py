"""Creates a HTML baseline report of a supplied PCAP file"""

# colour vars
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# import modules
import argparse
import sys
from collections import Counter
from scapy.all import rdpcap, TCP, UDP
import pyshark

# === Known services by port ===
PORT_SERVICE_MAP = {
    53: "DNS", 80: "HTTP", 443: "HTTPS", 123: "NTP", 22: "SSH", 25: "SMTP",
    110: "POP3", 143: "IMAP", 445: "SMB", 389: "LDAP", 3389: "RDP",
    67: "DHCP", 68: "DHCP", 21: "FTP", 20: "FTP", 3306: "MySQL",
    1433: "MSSQL", 5060: "SIP", 69: "TFTP", 161: "SNMP"
}

def get_service_name(pkt):
    if TCP in pkt or UDP in pkt:
        layer = pkt[TCP] if TCP in pkt else pkt[UDP]
        sport = layer.sport
        dport = layer.dport
        return PORT_SERVICE_MAP.get(sport) or PORT_SERVICE_MAP.get(dport)
    return None

def count_protocols(pcap_file):
    try:
        packets = rdpcap(pcap_file)
    except FileNotFoundError:
        print(f"File not found: {pcap_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading PCAP: {e}")
        sys.exit(1)

    protocol_counter = Counter()
    service_counter = Counter()

    for pkt in packets:
        if pkt.haslayer("IP"):
            proto = pkt["IP"].proto
            proto_name = {1: "ICMP", 6: "TCP", 17: "UDP"}.get(proto, f"IP_PROTO_{proto}")
            protocol_counter[proto_name] += 1

            service = get_service_name(pkt)
            if service:
                service_counter[service] += 1
        elif pkt.haslayer("ARP"):
            protocol_counter["ARP"] += 1
        else:
            protocol_counter["Other"] += 1

    return protocol_counter, service_counter

def extract_file_metadata(pcap_file):
    print("\nDetected file transfers (HTTP, FTP, SMB):")
    cap = pyshark.FileCapture(
        pcap_file,
        decode_as={'tcp.port==80': 'http', 'tcp.port==21': 'ftp-data', 'tcp.port==445': 'smb'},
        use_json=True,
        include_raw=False
    )

    for pkt in cap:
        try:
            if 'HTTP' in pkt:
                http = pkt.http
                content_length = getattr(http, 'content_length', None)
                disposition = getattr(http, 'content_disposition', '')
                filename = "Unknown"

                if "filename=" in disposition:
                    filename = disposition.split("filename=")[-1].strip('"; ')
                elif hasattr(http, 'request_uri'):
                    filename = http.request_uri.split("/")[-1] or "Unknown"

                if filename != "Unknown" or content_length:
                    print(f"[HTTP] Filename: {filename}, Size: {content_length or 'Unknown'} bytes")

            elif 'FTP' in pkt:
                ftp = pkt.ftp
                if hasattr(ftp, 'request_command') and ftp.request_command == 'RETR':
                    print(f"[FTP] File requested: {ftp.request_arg}")

            elif 'SMB' in pkt:
                smb = pkt.smb
                if hasattr(smb, 'file_name'):
                    print(f"[SMB] File accessed: {smb.file_name}")
        except Exception:
            continue

    cap.close()

def main():
    parser = argparse.ArgumentParser(description="Analyze PCAP: Protocols, Services, File Transfers.")
    parser.add_argument("file", type=str, help="Path to the PCAP file.")
    parser.add_argument("--top", type=int, help="Show only top N services.", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--extract-files", action="store_true", help="Try to extract file transfer metadata.")

    args = parser.parse_args()
    protocol_counts, service_counts = count_protocols(args.file)

    print("\nPacket counts by transport protocol:")
    for proto, count in protocol_counts.items():
        print(f"{proto}: {count}")

    sorted_services = service_counts.most_common(args.top) if args.top else service_counts.items()

    print("\nPacket counts by detected service:")
    for service, count in sorted_services:
        print(f"{service}: {count}")

    if args.extract_files:
        extract_file_metadata(args.file)

    if args.verbose:
        print(f"\nTotal packets parsed: {sum(protocol_counts.values())}")
        print(f"Unique services detected: {len(service_counts)}")

if __name__ == "__main__":
    main()
