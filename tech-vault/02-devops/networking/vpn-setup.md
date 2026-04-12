---
tags: [skill, devops, vpn]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [VPN, VPN Setup]
---

# VPN Setup

## Overview

VPN (Virtual Private Network) é a camada fundamental de conectividade segura em infraestruturas modernas. Para DevOps, VPN vai além de "tunel encriptado" — é sobre segmentação de rede, zero-trust networking, e integração com orquestração de containers. WireGuard revolucionou o espaço com sua implementação minimalista no kernel Linux, enquanto Tailscale abstraiu toda a complexidade de NAT traversal usando o mesmo protocolo.

> [!info] Escolha da Ferramenta
> WireGuard = controle total, máxima performance, complexidade manual de key exchange.
> Tailscale = WireGuard gerenciado, zero config NAT traversal, ideal para times remotos.
> OpenVPN = legacy, compatibilidade máxima, overhead maior de CPU.

---

## Core Concepts

### WireGuard — Configuração Completa

WireGuard opera na camada 3 (IP) com troca de chaves via Diffie-Hellman Curve25519. Cada peer tem um par de chaves pública/privada e uma lista de allowed IPs que define o roteamento.

**Geração de chaves:**
```bash
# Gerar par de chaves para servidor
wg genkey | tee server_private.key | wg pubkey > server_public.key

# Gerar par de chaves para cliente
wg genkey | tee client_private.key | wg pubkey > client_public.key

# Gerar preshared key (camada extra de segurança pós-quântica)
wg genpsk > preshared.key
```

**Configuração do servidor (`/etc/wireguard/wg0.conf`):**
```ini
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = <SERVER_PRIVATE_KEY>

# Habilitar IP forwarding para roteamento
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# Cliente 1
PublicKey = <CLIENT1_PUBLIC_KEY>
PresharedKey = <PRESHARED_KEY>
AllowedIPs = 10.0.0.2/32

[Peer]
# Cliente 2 — subnet router para rede interna 192.168.1.0/24
PublicKey = <CLIENT2_PUBLIC_KEY>
AllowedIPs = 10.0.0.3/32, 192.168.1.0/24
```

**Configuração do cliente:**
```ini
[Interface]
Address = 10.0.0.2/32
PrivateKey = <CLIENT_PRIVATE_KEY>
DNS = 10.0.0.1  # Resolver privado via VPN

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
PresharedKey = <PRESHARED_KEY>
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0   # Full tunnel — todo trafego via VPN
# AllowedIPs = 10.0.0.0/24  # Split tunnel — apenas trafego da VPN
PersistentKeepalive = 25  # Manter NAT aberto
```

**Gerenciamento de peers em runtime:**
```bash
# Adicionar peer sem reiniciar
wg set wg0 peer <PUBLIC_KEY> allowed-ips 10.0.0.4/32

# Remover peer
wg set wg0 peer <PUBLIC_KEY> remove

# Ver status de todos os peers
wg show wg0

# Ver estatísticas de trafego por peer
wg show wg0 transfer
```

### Tailscale — ACLs e Funcionalidades Avançadas

Tailscale usa um servidor de coordenação centralizado (control plane) mas o trafego de dados é peer-to-peer via WireGuard. A política de acesso é definida em HuJSON (JSON com comentários).

**ACL Policy completa (`tailscale-policy.hujson`):**
```json
{
  "acls": [
    // Desenvolvedores acessam todos os servidores de staging
    {
      "action": "accept",
      "src": ["group:developers"],
      "dst": ["tag:staging:*"]
    },
    // SREs têm acesso full a produção
    {
      "action": "accept",
      "src": ["group:sre"],
      "dst": ["tag:production:*"]
    },
    // Servidores podem se comunicar entre si na mesma tag
    {
      "action": "accept",
      "src": ["tag:production"],
      "dst": ["tag:production:*"]
    }
  ],
  "tagOwners": {
    "tag:production": ["group:sre"],
    "tag:staging": ["group:developers", "group:sre"]
  },
  "ssh": [
    {
      "action": "accept",
      "src": ["group:sre"],
      "dst": ["tag:production"],
      "users": ["root", "ubuntu"]
    }
  ]
}
```

**Exit nodes e subnet routers:**
```bash
# Configurar como subnet router (expoe rede local 192.168.1.0/24)
tailscale up --advertise-routes=192.168.1.0/24

# Aprovar subnet router via CLI admin
tailscale routes enable --host=<NODE_ID> --route=192.168.1.0/24

# Configurar como exit node (roteia trafego internet de outros peers)
tailscale up --advertise-exit-node

# Usar exit node em cliente
tailscale up --exit-node=<EXIT_NODE_IP> --exit-node-allow-lan-access
```

**MagicDNS e Split DNS:**
```bash
# Resolver nomes internos via Tailscale DNS
# Exemplo: postgres.tail123abc.ts.net resolve para IP do peer

# Configurar DNS customizado para dominio interno
tailscale dns nameservers add 10.0.0.53
tailscale dns search set internal.company.com
```

---

## Patterns

### Site-to-Site VPN

Conecta duas redes inteiras (ex: datacenter <-> AWS VPC). Ambos os lados atuam como gateways.

```
Office LAN (192.168.1.0/24) <--WireGuard--> AWS VPC (10.0.0.0/16)
         |                                          |
    wg0: 172.16.0.1                          wg0: 172.16.0.2
```

### Mesh Networking

Em vez de hub-and-spoke (todos passam pelo servidor), cada peer conecta diretamente aos outros. Tailscale faz isso automaticamente. Com WireGuard puro, cada par de peers precisa de configuração bilateral.

### Split Tunneling

Apenas trafego para redes específicas passa pela VPN. Trafego internet vai direto. Configurado via `AllowedIPs` no WireGuard.

```bash
# Split tunnel — apenas subnets internas
AllowedIPs = 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16

# Full tunnel — TUDO via VPN (incluindo internet)
AllowedIPs = 0.0.0.0/0, ::/0
```

### Docker Integration

```yaml
# docker-compose.yml com WireGuard como container
services:
  wireguard:
    image: lscr.io/linuxserver/wireguard:latest
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    environment:
      - PUID=1000
      - PGID=1000
      - SERVERURL=vpn.example.com
      - SERVERPORT=51820
      - PEERS=client1,client2,client3
      - PEERDNS=auto
      - INTERNAL_SUBNET=10.13.13.0
    volumes:
      - ./config:/config
      - /lib/modules:/lib/modules
    ports:
      - 51820:51820/udp
    sysctls:
      - net.ipv4.conf.all.src_valid_mark=1
    restart: unless-stopped

  # Servico que roteia trafego PELO container WireGuard
  app:
    image: myapp:latest
    network_mode: "service:wireguard"  # Compartilha network namespace
    depends_on:
      - wireguard
```

### Kubernetes VPN Sidecar

```yaml
# Pod com sidecar WireGuard para comunicacao segura com servicos externos
apiVersion: v1
kind: Pod
metadata:
  name: app-with-vpn
spec:
  initContainers:
    - name: wireguard-init
      image: masipcat/wireguard-go:latest
      securityContext:
        capabilities:
          add: ["NET_ADMIN"]
      volumeMounts:
        - name: wireguard-config
          mountPath: /etc/wireguard
      command: ["wg-quick", "up", "wg0"]
  containers:
    - name: app
      image: myapp:latest
      # App usa a interface wg0 criada pelo initContainer
  volumes:
    - name: wireguard-config
      secret:
        secretName: wireguard-config
```

---

## Gotchas

> [!warning] MTU e Fragmentacao
> WireGuard adiciona overhead de ~60 bytes por pacote. Se a interface fisica tem MTU 1500, configure `MTU = 1420` na interface WireGuard para evitar fragmentacao, especialmente com IPv6 (overhead maior).

> [!warning] AllowedIPs nao e Firewall
> `AllowedIPs` no WireGuard define o roteamento (quais IPs sao encaminhados pelo tunnel), NAO controle de acesso. Para firewall real, use iptables/nftables separadamente.

> [!bug] Tailscale + Docker NAT
> Containers Docker com `bridge` network nao sao alcancaveis via Tailscale subnet routing por padrao. Use `--accept-routes` e configure proxy ARP ou use `host` network mode nos containers.

> [!tip] Key Rotation
> WireGuard nao tem mecanismo nativo de rotacao de chaves. Implemente rotacao periodica gerando novos pares e atualizando peers via scripts automatizados ou ferramentas como [[secrets-management]] (HashiCorp Vault).

---

## Snippets

```bash
# Script de adicao automatica de peers
#!/bin/bash
PEER_PUBKEY=$(wg genkey | tee /tmp/peer_priv.key | wg pubkey)
PEER_IP="10.0.0.$(( $(wg show wg0 peers | wc -l) + 2 ))"

wg set wg0 peer "$PEER_PUBKEY" allowed-ips "${PEER_IP}/32"
wg-quick save wg0

echo "Peer adicionado: IP=$PEER_IP, PubKey=$PEER_PUBKEY"
```

```bash
# Monitoramento de peers inativos
wg show wg0 latest-handshakes | while read peer timestamp; do
  age=$(( $(date +%s) - timestamp ))
  if [ $age -gt 300 ]; then
    echo "WARN: Peer $peer sem handshake ha ${age}s"
  fi
done
```

---

## References

- [WireGuard Official Docs](https://www.wireguard.com/)
- [Tailscale ACL Docs](https://tailscale.com/kb/1018/acls/)
- [WireGuard Whitepaper](https://www.wireguard.com/papers/wireguard.pdf)

---

## Related

- [[reverse-proxy]] — Expor servicos via proxy atras da VPN
- [[dns-and-cdn]] — DNS privado integrado com VPN (MagicDNS, Pi-hole)
- [[kubernetes-basics]] — VPN sidecars em pods Kubernetes
- [[terraform]] — Provisionar infraestrutura de VPN como codigo
- [[secrets-management]] — Gerenciar chaves WireGuard com Vault/SOPS
