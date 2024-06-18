import os
import sys
import socket
import ipaddress
from ip import IP
from icmp import ICMP

MESSAGE = '0xSAH3R!7'


class Scanner:
    def __init__(self, host, SUBNET):

        if os.name == 'nt':
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP

        self.host = host
        self.SUBNET = SUBNET
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        self.socket.bind((host, 0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if os.name == 'nt':
            # check if running Windows OS then, send additional IOCTL to network card driver to enable promiscuous mode
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
            print('\n[*] Windows OS detected, promiscuous mode has enabled...')

    def sniff(self):
        hosts_up = {f'{str(self.host)} *'}
        try:
            while True:
                raw_buffer = self.socket.recvfrom(65535)[0]  # read a packet
                ip_header = IP(raw_buffer[0:20])  # create an IP header from the first 20 bytes

                # check if it's ICMP, deal with
                if ip_header.protocol == "ICMP":
                    offset = ip_header.ihl * 4
                    buf = raw_buffer[offset:offset + 8]
                    icmp_header = ICMP(buf)

                    # check for TYPE 3 and CODE
                    if icmp_header.code == 3 and icmp_header.type == 3:
                        if ipaddress.ip_address(ip_header.src_address) in ipaddress.IPv4Network(self.SUBNET):
                            if raw_buffer[len(raw_buffer) - len(MESSAGE):] == bytes(MESSAGE, 'utf-8'):
                                hosts_up.add(str(ip_header.src_address))
                                print(f'» Host Up: {str(ip_header.src_address)}')

        except KeyboardInterrupt:
            if os.name == 'nt':
                self.socket.ioctl(socket.SIO_RCVALL,
                                  socket.RCVALL_OFF)  # turn off promiscuous mode after executing the script
            if hosts_up:
                print("\n\n═════════════════════════════════════")
                print(f'Summary: Hosts up on {self.SUBNET}')
            for host in sorted(hosts_up):
                print(f'{host}')
            print('\nFinished!\n')
            sys.exit(0)
