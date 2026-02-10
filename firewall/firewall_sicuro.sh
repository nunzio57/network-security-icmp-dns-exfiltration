
nft flush ruleset

echo "[*] Configuro le regole NFTABLES (Mitigazione)..."

nft -f - <<EOF
table ip filter{
    # Definizione set dinamico per host che effettuano tunneling
    set tunnelers{
        type ipv4_addr
        flags timeout
    }

    chain input{
        type filter hook input priority 0; policy drop;

        ct state { established, related } accept
        iif "lo" accept
        tcp dport 22 accept
    }

    chain forward{
        type filter hook forward priority 0; policy drop;
        
        # Blocco traffico da host identificati come tunnelers
        ip saddr @tunnelers counter drop

        # Consente traffico HTTP inbound verso la DMZ
        iifname "enp0s3" oifname "enp0s8" ip daddr 10.0.10.100 tcp dport 80 accept

        # REGOLE MITIGAZIONE ICMP
        # 1. Rate Limiting: max 1 ping/s, altrimenti ban di 60s
        iifname "enp0s8" oifname "enp0s3" icmp type echo-request limit rate over 1/second update @tunnelers { ip saddr timeout 60s } counter log prefix "BLOCK_ICMP_SIZE_MAX: " drop
        
        # 2. Controllo dimensionale del payload ICMP
        iifname "enp0s8" oifname "enp0s3" icmp type echo-request meta length > 100 counter log prefix "BLOCK_ICMP_SIZE_MAX: " drop
        iifname "enp0s8" oifname "enp0s3" icmp type echo-request meta length < 70 counter log prefix "BLOCK_ICMP_SIZE_MIN: " drop
        
        # 3. DPI: Blocco stringa "root" (0x726f6f74) nel payload
        iifname "enp0s8" oifname "enp0s3" icmp type echo-request @th,48,128 0x726f6f74 counter log prefix "DPI_CONTENT_ROOT: " drop
        
        # 4. Protezione da ICMP Flood generico
        iifname "enp0s8" oifname "enp0s3" icmp type echo-request counter log prefix "FLOOD_DETECTED: " drop

        ct state { established, related } accept

        # REGOLE MITIGAZIONE DNS
        # 1. DPI: Blocco sottodomini (labels) troppo lunghi (> 25 chars)
        iifname "enp0s8" oifname "enp0s3" udp dport 53 @th,160,8 > 25 counter log prefix "DPI_MALWARE_BLOCK: " drop
        
        # 2. Metering: Protezione da DNS Flood con ban automatico
        iifname "enp0s8" oifname "enp0s3" udp dport 53 meter flood_protection { ip saddr limit rate over 1/second } update @tunnelers { ip saddr } counter log prefix "PERM_BAN_ACTIVATED: " drop

        # 3. Filtro dimensionale query DNS
        iifname "enp0s8" oifname "enp0s3" udp dport 53 meta length < 90 accept
        iifname "enp0s8" oifname "enp0s3" udp dport 53 counter log prefix "DNS_SIZE_BLOCK: " drop

        # Regole di fallback per traffico legittimo residuo
        iifname "enp0s8" oifname "enp0s3" icmp type echo-request accept
        iifname "enp0s8" oifname "enp0s3" udp dport 53 accept
        iifname "enp0s8" oifname "enp0s3" tcp dport 53 accept
    }

    chain output{
        type filter hook output priority 0; policy accept;
    }
}

table ip nat{
    chain postrouting{
        type nat hook postrouting priority -100; policy accept;
        
        # DNS Enforcement: Reindirizza forzatamente tutto il traffico DNS a Google DNS
        iifname "enp0s8" udp dport 53 dnat to 8.8.8.8
        iifname "enp0s8" tcp dport 53 dnat to 8.8.8.8
    }

    chain prerouting{
        type nat hook prerouting priority -100; policy accept;
    }
}
EOF

echo "[*] Firewall HARDENED attivo."
echo "[*] Policy: DROP ALL"
echo "[*] Allowed: HTTP inbound, ICMP/DNS Outbound (Filtrati)"