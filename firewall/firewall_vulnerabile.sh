#!/bin/bash

IF_WAN="enp0s3"
IF_DMZ="enp0s8"

sysctl -w net.ipv4.ip_forward=1

echo "Pulizia regole esistenti..."
iptables -F
iptables -t nat -F
iptables -X

iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

echo "Policy di Default impostata su DROP"

iptables -t nat -A POSTROUTING -o $IF_WAN -j MASQUERADE

iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

iptables -A FORWARD -i $IF_WAN -o $IF_DMZ -p tcp --dport 80 -d 10.0.10.100 -j ACCEPT
echo "ACCESSO HTTP dall'esterno consentito verso DMZ"

#iptables -A FORWARD -i enp0s8 -o enp0s3 -p tcp --dport 80 -j ACCEPT
iptables -A FORWARD -i $IF_DMZ -o $IF_WAN -p tcp --dport 80 -d 10.0.10.100 -j ACCEPT
iptables -A FORWARD -i $IF_DMZ -o $IF_WAN -p icmp -j ACCEPT
iptables -A FORWARD -i $IF_DMZ -o $IF_WAN -p udp --dport 53 -j ACCEPT

echo "VULNERABILITA ATTIVE: DNS(UDP 53) e ICMP in uscita dalla DMZ permessi"
echo "Firewall Configurato!"