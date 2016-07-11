#!/usr/bin/env python3
# encoding: UTF-8

import socket
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

SSDP_BROADCAST_PORT = 1900
SSDP_BROADCAST_ADDR = "239.255.255.250"

SSDP_BROADCAST_PARAMS = ["M-SEARCH * HTTP/1.1",
                         "HOST: {}:{}".format(SSDP_BROADCAST_ADDR,
                                              SSDP_BROADCAST_PORT),
                         "MAN: \"ssdp:discover\"",
                         "MX: 10",
                         "ST: ssdp:all", "", ""]
SSDP_BROADCAST_MSG = "\r\n".join(SSDP_BROADCAST_PARAMS)


def get_devices(timeout=3.0):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
    s.bind(("", SSDP_BROADCAST_PORT+10))
    
    s.sendto(bytes(SSDP_BROADCAST_MSG, "UTF-8"), (SSDP_BROADCAST_ADDR, 
                                                  SSDP_BROADCAST_PORT))
    s.settimeout(timeout)
    
    devices = []
    while True:

        try:
            data, addr = s.recvfrom(1024)
        except socket.timeout:
            break

        try:
            info = [a.split(":", 1) for a in data.decode("UTF-8").split("\r\n")[1:]]
            device = dict([(a[0].strip().lower(), a[1].strip()) for a in info if len(a) >= 2])
            devices.append(device)
        except:
            pass

    devices = [device for device in devices if "AVTransport" in device["st"]]

    for i in range(len(devices)):

        location_url = devices[i]["location"]
        xml = urllib.request.urlopen(location_url).read().decode("UTF-8")
        xml = re.sub(" xmlns=\"[^\"]+\"", "", xml, count=1)
        info = ET.fromstring(xml)

        location = urllib.parse.urlparse(location_url)
        hostname = location.hostname
        port = location.port
        path = info.find(
            "./device/serviceList/service/[serviceType='{}']/controlURL".format(
                devices[i]["st"]
            )
        ).text
        action_url = urllib.parse.urljoin(location_url, path)

        devices[i].update({
            "info"      : info,
            "hostname"  : hostname,
            "action_url": action_url
        })

    return devices


if __name__ == "__main__":

    import sys
    import json

    timeout = int(sys.argv[1]) if len(sys.argv) >= 2  else 5

    devices = get_devices(timeout)

    for i, device in enumerate(devices, 1):
        device["info"] = "..."
        print("Device {}:\n{}\n\n".format(i, json.dumps(device, indent=4)))

