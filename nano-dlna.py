#!/usr/bin/env python3
# encoding: UTF-8

import socket

SSDP_BROADCAST_PORT = 1900
SSDP_BROADCAST_ADDR = "239.255.255.250"

SSDP_BROADCAST_PARAMS = ["M-SEARCH * HTTP/1.1",
                         "HOST: {}:{}".format(SSDP_BROADCAST_ADDR,
                                              SSDP_BROADCAST_PORT),
                         "MAN: \"ssdp:discover\"",
                         "MX: 10",
                         "ST: ssdp:all", "", ""]
SSDP_BROADCAST_MSG = "\r\n".join(SSDP_BROADCAST_PARAMS)
 

def get_devices():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
    s.bind(("", SSDP_BROADCAST_PORT))
    
    s.sendto(bytes(SSDP_BROADCAST_MSG, "UTF-8"), (SSDP_BROADCAST_ADDR, SSDP_BROADCAST_PORT))
    
    devices = []

    while True:
        data, addr = s.recvfrom(1024)
        info = [a.split(":", 1) for a in data.decode("UTF-8").split("\r\n")[1:]]
        device = dict([(a[0].strip(), a[1].strip()) for a in info if len(a) >= 2])
        devices.append(device)
        print(info)

    return devices


def set_stream_server():
    pass

def play():
    pass

