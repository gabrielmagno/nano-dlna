#!/usr/bin/env python3
# encoding: UTF-8

import re
import socket
import sys
import xml.etree.ElementTree as ET

if sys.version_info.major == 3:
    import urllib.request as urllibreq
    import urllib.parse as urllibparse
else:
    import urllib2 as urllibreq
    import urlparse as urllibparse

import logging
import json

SSDP_BROADCAST_PORT = 1900
SSDP_BROADCAST_ADDR = "239.255.255.250"

SSDP_BROADCAST_PARAMS = [
    "M-SEARCH * HTTP/1.1",
    "HOST: {0}:{1}".format(SSDP_BROADCAST_ADDR, SSDP_BROADCAST_PORT),
    "MAN: \"ssdp:discover\"", "MX: 10", "ST: ssdp:all", "", ""]
SSDP_BROADCAST_MSG = "\r\n".join(SSDP_BROADCAST_PARAMS)

UPNP_DEFAULT_SERVICE_TYPE = "urn:schemas-upnp-org:service:AVTransport:1"


def register_device(location_url):

    xml = urllibreq.urlopen(location_url).read().decode("UTF-8")
    xml = re.sub(" xmlns=\"[^\"]+\"", "", xml, count=1)
    info = ET.fromstring(xml)

    location = urllibparse.urlparse(location_url)
    hostname = location.hostname

    friendly_name = info.find("./device/friendlyName").text

    try:
        path = info.find(
            "./device/serviceList/service/"
            "[serviceType='{0}']/controlURL".format(
                UPNP_DEFAULT_SERVICE_TYPE
            )
        ).text
        action_url = urllibparse.urljoin(location_url, path)
    except AttributeError:
        action_url = None

    device = {
        "location": location_url,
        "hostname": hostname,
        "friendly_name": friendly_name,
        "action_url": action_url,
        "st": UPNP_DEFAULT_SERVICE_TYPE
    }

    logging.debug(
        "Device registered: {}".format(
            json.dumps({
                "device_xml": xml,
                "device_info": device
            })
        )
    )

    return device


def get_devices(timeout=3.0):

    logging.debug("Configuring broadcast message")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
    s.bind(("", SSDP_BROADCAST_PORT + 10))

    logging.debug("Sending broadcast message")
    s.sendto(SSDP_BROADCAST_MSG.encode("UTF-8"), (SSDP_BROADCAST_ADDR,
                                                  SSDP_BROADCAST_PORT))

    logging.debug("Waiting for devices ({} seconds)".format(timeout))
    s.settimeout(timeout)

    devices = []
    while True:

        try:
            data, addr = s.recvfrom(1024)
        except socket.timeout:
            break

        try:
            info = [a.split(":", 1)
                    for a in data.decode("UTF-8").split("\r\n")[1:]]
            device = dict([(a[0].strip().lower(), a[1].strip())
                           for a in info if len(a) >= 2])
            devices.append(device)
            logging.debug(
                "Device broadcast response: {}".format(
                    json.dumps({
                        "broadcast_message_raw": data.decode("UTF-8"),
                        "broadcast_message_info": device
                    })
                )
            )
        except Exception:
            pass

    devices_urls = [dev["location"]
                    for dev in devices if "AVTransport" in dev["st"]]
    devices = [register_device(location_url) for location_url in devices_urls]

    return devices


if __name__ == "__main__":

    timeout = int(sys.argv[1]) if len(sys.argv) >= 2 else 5

    devices = get_devices(timeout)

    for i, device in enumerate(devices, 1):
        print("Device {0}:\n{1}\n\n".format(i, json.dumps(device, indent=4)))
