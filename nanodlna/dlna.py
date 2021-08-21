#!/usr/bin/env python3
# encoding: UTF-8

import os
import pkgutil
import sys
from xml.sax.saxutils import escape as xmlescape

if sys.version_info.major == 3:
    import urllib.request as urllibreq
else:
    import urllib2 as urllibreq

import traceback
import logging
import json


def send_dlna_action(device, data, action):

    logging.debug("Sending DLNA Action: {}".format(
        json.dumps({
            "action": action,
            "device": device,
            "data": data
        })
    ))

    action_data = pkgutil.get_data(
        "nanodlna", "templates/action-{0}.xml".format(action)).decode("UTF-8")
    action_data = action_data.format(**data).encode("UTF-8")

    headers = {
        "Content-Type": "text/xml; charset=\"utf-8\"",
        "Content-Length": "{0}".format(len(action_data)),
        "Connection": "close",
        "SOAPACTION": "\"{0}#{1}\"".format(device["st"], action)
    }

    logging.debug("Sending DLNA Request: {}".format(
        json.dumps({
            "url": device["action_url"],
            "data": action_data.decode("UTF-8"),
            "headers": headers
        })
    ))

    try:
        request = urllibreq.Request(device["action_url"], action_data, headers)
        urllibreq.urlopen(request)
        logging.debug("Request sent")
    except Exception:
        logging.error("Unknown error sending request: {}".format(
            json.dumps({
                "url": device["action_url"],
                "data": action_data.decode("UTF-8"),
                "headers": headers,
                "error": traceback.format_exc()
            })
        ))


def play(files_urls, device):

    logging.debug("Starting to play: {}".format(
        json.dumps({
            "files_urls": files_urls,
            "device": device
        })
    ))

    video_data = {
        "uri_video": files_urls["file_video"],
        "type_video": os.path.splitext(files_urls["file_video"])[1][1:],
    }

    if "file_subtitle" in files_urls and files_urls["file_subtitle"]:

        video_data.update({
            "uri_sub": files_urls["file_subtitle"],
            "type_sub": os.path.splitext(files_urls["file_subtitle"])[1][1:]
        })

        metadata = pkgutil.get_data(
            "nanodlna",
            "templates/metadata-video_subtitle.xml").decode("UTF-8")
        video_data["metadata"] = xmlescape(metadata.format(**video_data))

    else:
        video_data["metadata"] = ""

    logging.debug("Created video data: {}".format(json.dumps(video_data)))

    logging.debug("Setting Video URI")
    send_dlna_action(device, video_data, "SetAVTransportURI")
    logging.debug("Playing video")
    send_dlna_action(device, video_data, "Play")
