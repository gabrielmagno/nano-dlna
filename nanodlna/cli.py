#!/usr/bin/env python3

import sys
import os
import argparse
import json

from nanodlna import *

def get_subtitle(file_video):

    video, extension = os.path.splitext(file_video)

    file_subtitle = "{}.srt".format(video)

    if os.path.exists(file_subtitle):
        return file_subtitle
    else:
        return None
    

def list_devices(args):

    my_devices = devices.get_devices(args.timeout)

    for i, device in enumerate(my_devices, 1):
        device["info"] = "..."
        print("Device {}:\n{}\n\n".format(i, json.dumps(device, indent=4)))


def play(args):

    # Get video and subtitle file names

    files = { "file_video" : args.file_video }

    if args.use_subtitle:

        if not args.file_subtitle:
            args.file_subtitle = get_subtitle(args.file_video)

        if args.file_subtitle:
            files["file_subtitle"] = args.file_subtitle


    # Select device to play

    my_devices = devices.get_devices(args.timeout)

    if len(my_devices) > 0:
        if args.device_query:
            device = [ device for device in my_devices 
                           if args.device_query in str(device).lower() ][0]
        else:
            device = my_devices[0]
    else:
        sys.exit("No devices found.")


    # Configure streaming server

    target_ip = device["hostname"]
    serve_ip = streaming.get_serve_ip(target_ip)
    files_urls = streaming.start_server(files, serve_ip)


    # Play the video through DLNA protocol 

    dlna.play(files_urls, device)


def run():

    parser = argparse.ArgumentParser(description="A minimal UPnP/DLNA media streamer.")
    parser.add_argument("-t", "--timeout", type=float, default=5)
    subparsers = parser.add_subparsers(dest="subparser_name")

    p_list = subparsers.add_parser('list')
    p_list.set_defaults(func=list_devices)

    p_play = subparsers.add_parser('play')
    p_play.add_argument("-d", "--device", dest="device_query")
    p_play.add_argument("-s", "--subtitle", dest="file_subtitle")
    p_play.add_argument("-n", "--no-subtitle", dest="use_subtitle", action="store_false")
    p_play.add_argument("file_video")
    p_play.set_defaults(func=play)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":

    run()

