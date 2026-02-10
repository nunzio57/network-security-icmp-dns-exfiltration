from scapy.all import sniff, DNS, DNSQR
import binascii

IFACE = "eth0"  

print("[*] In ascolto su UDP 53 (DNS Tunnel)...")

def process(pkt):
    if pkt.haslayer(DNSQR):
        qname = pkt[DNSQR].qname.decode()
        if ".google.com" in qname:
            data = qname.split(".google.com")[0]
            if "eof" in data:
                print("\n[+] TRASFERIMENTO COMPLETATO!")
            else:
                print(f"[Ricevuto] {data}")

sniff(filter="udp port 53", iface=IFACE, prn=process, store=0)