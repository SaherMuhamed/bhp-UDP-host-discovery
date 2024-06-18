import ipaddress
import socket
import sys
import threading
import time
from scanner import Scanner, MESSAGE
from art import ascii_art

if sys.version_info < (3, 0):
    sys.stderr.write("\nYou need python 3.0 or later to run this script\n")
    sys.stderr.write(
        "Please update and make sure you use the command python3 udp_scan.py <host_ip> <target_subnet>\n\n")
    sys.exit(0)


def udp_sender():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(sys.argv[2]).hosts():
            sender.sendto(bytes(MESSAGE, 'utf-8'), (str(ip), 65212))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("[+] Usage: %s <host_ip> <target_subnet>" % sys.argv[0])
        print("[+] Example: %s 192.168.1.7 192.168.1.0/24" % sys.argv[0] + "\n")
        sys.exit(-1)
    print(ascii_art)
    print("\t  » » Scanning « « \n═════════════════════════════════════")
    s = Scanner(host=sys.argv[1], SUBNET=sys.argv[2])
    time.sleep(7)
    t = threading.Thread(target=udp_sender)
    t.start()
    s.sniff()
