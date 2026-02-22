# Data Exfiltration via ICMP and DNS Tunneling

**Exam Project — Network Security**
University of Naples Federico II
A.Y. 2025/2026

Professor: Simon Pietro Romano
Author:Nunzio Giordano (M63001707)

---

## Overview

This project demonstrates how fundamental network protocols (ICMP and DNS), typically allowed through firewalls to ensure basic connectivity, can be exploited as covert channels to exfiltrate sensitive data from a compromised network. A defensive configuration based on nftables is then implemented to detect and block these techniques.

## Architecture

The environment consists of three virtual machines:

| Machine | OS | Role | IP |
|---|---|---|---|
| Attacker | Kali Linux | External malicious actor (Internet) | 192.168.66.66 |
| Firewall | Ubuntu Server | Gateway between WAN and DMZ, two network interfaces (enp0s3, enp0s8) | — |
| Victim | Ubuntu Desktop | Apache web server in the DMZ | 10.0.10.100 |

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  KALI LINUX  │      │   FIREWALL   │      │  DMZ (Ubuntu) │
│ 192.168.66.66├──────┤ enp0s3  enp0s8├──────┤ 10.0.10.100  │
│  (Attacker)  │WAN   │              │  DMZ │  (Victim)     │
└──────────────┘      └──────────────┘      └──────────────┘
```

## Project Phases

### 1. Vulnerable Firewall Configuration

iptables-based firewall with a default DROP policy, but with permissive outbound rules for ICMP and DNS (UDP 53). No payload inspection, no rate limiting, no restrictions on destination DNS servers.

### 2. Initial Compromise

Exploitation of an RCE vulnerability in the Apache web server's `index.php`. The GET parameter `cmd` is passed directly to `system()` without any sanitization, allowing arbitrary command execution with `www-data` privileges.

### 3. Exfiltration via ICMP Tunneling

Three coordinated Python scripts:

- **`icmp_sender.py`** (Victim) — Scans the filesystem, identifies files readable by the current user, and sends a report to the attacker via ICMP Echo Request packets. Data is fragmented into 32-byte chunks and tagged with ID 1337.

- **`stealer.py`** (Victim) — Reads a target file in binary mode, fragments it, and exfiltrates it via ICMP Echo Request with ID 9999. Includes a custom header and an EOF signal to delimit the transmission.

- **`icmp_receiver.py`** (Attacker) — Scapy-based sniffer listening for ICMP traffic. Filters packets by type (Echo Request) and Raw layer presence, decodes the payload, and reconstructs the data.

### 4. Exfiltration via DNS Tunneling

Three components:

- **`injector.py`** (Attacker) — Automated dropper. Encodes the malware in Base64, splits it into 500-character chunks, and transfers it to the victim through HTTP requests to the vulnerable page, reconstructing the original file on the target.

- **`dns_stealer.py`** (Victim) — Malware using only Python standard libraries (socket). Manually constructs DNS packets at the byte level, converts file contents to hexadecimal, and encapsulates them as subdomains in fake DNS queries (`<hex_data>.google.com`). Sends over UDP 53 to the attacker.

- **`dns_receiver.py`** (Attacker) — Sniffer on UDP 53. Extracts the QNAME from queries, isolates the subdomain containing the hex-encoded data, and signals completion upon receiving the "eof" marker.

### 5. Mitigation with nftables

Replacement of iptables with nftables to implement advanced defenses:

**Dynamic Blacklisting** — `@tunnelers` set with timeout. IPs that violate rules are automatically added to a temporary blacklist (60s) that blocks all their traffic.

**ICMP Anti-Tunneling:**
- Rate limiting: max 1 ping/second, exceeding = ban
- Size checking: packets accepted only between 70 and 100 bytes
- Deep Packet Inspection: blocks packets containing the string "root" (`0x726f6f74`) in the payload

**DNS Anti-Exfiltration:**
- Size checking: queries accepted only under 90 bytes
- DPI on label length: blocked if the first subdomain exceeds 25 characters
- Rate limiting with dynamic meter: exceeding = insertion into global blacklist
- DNS enforcement via DNAT: all port 53 traffic forcefully redirected to 8.8.8.8

## Requirements

- VirtualBox (or equivalent) for the VMs
- Python 3 with Scapy (`pip install scapy`)
- Apache2 with PHP on the victim server
- Wireshark for traffic analysis

## Disclaimer

This project was developed for educational purposes as part of the Network Security course. The demonstrated techniques must only be used in controlled and authorized environments.
