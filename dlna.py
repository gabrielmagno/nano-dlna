#!/usr/bin/env python3
# encoding: UTF-8

import os
import http.server
import urllib.parse 
import urllib.request
import html

data_path = "data"

def send_dlna_action(device, data, action):

    with open("{}/action-{}.xml".format(data_path, action), "r") as infile:
        action_data = infile.read().format(**data).encode("UTF-8")

    headers = { 
      "Content-Type"   : "text/xml; charset=\"utf-8\"",
      "Content-Length" : "{}".format(len(action_data)),
      "Connection"     : "close",
      "SOAPACTION"     : "\"{}#{}\"".format(device["st"], action)
    } 

    request = urllib.request.Request(device["action_url"], action_data, headers)
    urllib.request.urlopen(request)


def play(files_urls, device):

    video_data = {
        "uri_video"  : files_urls["file_video"],
        "type_video" : os.path.splitext(files_urls["file_video"])[1][1:],
    }

    if "file_subtitle" in files_urls:

        video_data.update({
            "uri_sub"    : files_urls["file_subtitle"],
            "type_sub"   : os.path.splitext(files_urls["file_subtitle"])[1][1:]
        })

        with open("{}/metadata-video_subtitle.xml".format(data_path), "r") as infile:
            video_data["metadata"] = html.escape(infile.read().format(**video_data))

    else:
        video_data["metadata"] = ""

    send_dlna_action(device, video_data, "SetAVTransportURI")
    send_dlna_action(device, video_data, "Play")

