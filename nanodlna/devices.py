#!/usr/bin/env python3
# encoding: UTF-8

import re
import socket
import struct
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

UPNP_DEVICE_TYPE = "urn:schemas-upnp-org:device:MediaRenderer:1"
UPNP_SERVICE_TYPE = "urn:schemas-upnp-org:service:AVTransport:1"


def get_xml_field_text(xml_root, query):
    result = None
    if xml_root:
        node = xml_root.find(query)
        result = node.text if node is not None else None
    return result


def register_device(location_url):

    xml_raw = urllibreq.urlopen(location_url).read().decode("UTF-8")
    logging.debug(
        "Device to be registered: {}".format(
            json.dumps({
                "location_url": location_url,
                "xml_raw": xml_raw
            })
        )
    )

    xml = re.sub(r"""\s(xmlns="[^"]+"|xmlns='[^']+')""", '', xml_raw, count=1)
    info = ET.fromstring(xml)

    location = urllibparse.urlparse(location_url)
    hostname = location.hostname

    device_root = info.find("./device")
    if not device_root:
        device_root = info.find(
            "./device/deviceList/device/"
            "[deviceType='{0}']".format(
                UPNP_DEVICE_TYPE
            )
        )

    friendly_name = get_xml_field_text(device_root, "./friendlyName")
    manufacturer = get_xml_field_text(device_root, "./manufacturer")
    action_url_path = get_xml_field_text(
        device_root,
        "./serviceList/service/"
        "[serviceType='{0}']/controlURL".format(
            UPNP_SERVICE_TYPE
        )
    )

    if action_url_path is not None:
        action_url = urllibparse.urljoin(location_url, action_url_path)
    else:
        action_url = None

    device = {
        "location": location_url,
        "hostname": hostname,
        "manufacturer": manufacturer,
        "friendly_name": friendly_name,
        "action_url": action_url,
        "st": UPNP_SERVICE_TYPE
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


def remove_duplicates(devices):
    seen = set()
    result_devices = []
    for device in devices:
        device_str = str(device)
        if device_str not in seen:
            result_devices.append(device)
            seen.add(device_str)
    return result_devices


def get_devices(timeout=3.0, host=None):

    if not host:
        host = "0.0.0.0"
    logging.debug("Searching for devices on {}".format(host))

    logging.debug("Configuring broadcast message")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # OpenBSD needs the ttl for the IP_MULTICAST_TTL as an unsigned char
    ttl = struct.pack("B", 4)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    s.bind((host, 0))

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

    devices_urls = [
        dev["location"]
        for dev in devices
        if "st" in dev and
           "AVTransport" in dev["st"]
    ]

    devices = [
        register_device(location_url)
        for location_url in devices_urls
    ]

    devices = remove_duplicates(devices)

    return devices


if __name__ == "__main__":

    timeout = int(sys.argv[1]) if len(sys.argv) >= 2 else 5

    devices = get_devices(timeout, "0.0.0.0")

    for i, device in enumerate(devices, 1):
        print("Device {0}:\n{1}\n\n".format(i, json.dumps(device, indent=4)))
