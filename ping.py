#!/usr/bin/env python3
"""QuickPing – minimal ICMP ping utility.

Usage:
    python ping.py <host> [count]

Example:
    python ping.py example.com 4
"""
import sys
import socket
import struct
import time
import os

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
DEFAULT_COUNT = 4
TIMEOUT = 1

def checksum(source_bytes):
    """Calculate the Internet Checksum of the given data.
    The checksum is the 16-bit one's complement of the one's complement sum of all 16-bit words.
    """
    sum = 0
    count_to = (len(source_bytes) // 2) * 2
    count = 0
    while count < count_to:
        this_val = source_bytes[count + 1] * 256 + source_bytes[count]
        sum = sum + this_val
        sum = sum & 0xffffffff
        count += 2
    if count_to < len(source_bytes):
        sum += source_bytes[-1]
        sum = sum & 0xffffffff
    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)
    answer = ~sum & 0xffff
    answer = socket.htons(answer)
    return answer

def create_packet(id):
    """Create a new ICMP echo request packet with the given id."""
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = struct.pack('d', time.time())
    chk = checksum(header + data)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, chk, id, 1)
    return header + data

def ping(host, count=DEFAULT_COUNT):
    try:
        dest_addr = socket.gethostbyname(host)
    except socket.gaierror as e:
        print(f"Cannot resolve {host}: {e}")
        return

    print(f"PING {host} ({dest_addr}): {count} packets")
    delays = []
    for seq in range(count):
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            sock.settimeout(TIMEOUT)
            packet_id = os.getpid() & 0xFFFF
            packet = create_packet(packet_id)
            send_time = time.time()
            try:
                sock.sendto(packet, (dest_addr, 1))
                recv_packet, _ = sock.recvfrom(1024)
                recv_time = time.time()
            except socket.timeout:
                print(f"Request timed out.")
                continue
            icmp_header = recv_packet[20:28]
            type, code, checksum_recv, p_id, sequence = struct.unpack('bbHHh', icmp_header)
            if p_id != packet_id:
                continue
            delay = (recv_time - send_time) * 1000  # ms
            delays.append(delay)
            print(f"Reply from {dest_addr}: time={delay:.2f} ms")
        time.sleep(1)
    if delays:
        avg = sum(delays) / len(delays)
        print(f"--- {host} ping statistics ---")
        print(f"{len(delays)} packets transmitted, {len(delays)} received, {100 - (len(delays)/count*100):.0f}% packet loss")
        print(f"Average latency: {avg:.2f} ms")
    else:
        print("All requests timed out.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python ping.py <host> [count]")
        sys.exit(1)
    host_arg = sys.argv[1]
    count_arg = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_COUNT
    ping(host_arg, count_arg)
