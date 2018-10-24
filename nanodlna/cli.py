#!/usr/bin/env python3

from __future__ import print_function

import argparse
import json
import os
import sys

from . import devices, dlna, streaming


def get_subtitle(file_video):

    video, extension = os.path.splitext(file_video)

    file_subtitle = "{0}.srt".format(video)

    if not os.path.exists(file_subtitle):
        return None
    return file_subtitle


def list_devices(args):

    my_devices = devices.get_devices(args.timeout)

    for i, device in enumerate(my_devices, 1):
        print("Device {0}:\n{1}\n\n".format(i, json.dumps(device, indent=4)))


def play(args):

    # Get video and subtitle file names

    files = {"file_video": args.file_video}

    if args.use_subtitle:

        if not args.file_subtitle:
            args.file_subtitle = get_subtitle(args.file_video)

        if args.file_subtitle:
            files["file_subtitle"] = args.file_subtitle

    # Select device to play
    device = None

    if args.device_url:
        device = devices.register_device(args.device_url)
    else:
        my_devices = devices.get_devices(args.timeout)

        if len(my_devices) > 0:
            if args.device_query:
                device = [
                    device for device in my_devices
                    if args.device_query.lower() in str(device).lower()][0]
            else:
                device = my_devices[0]

    if not device:
        sys.exit("No devices found.")

    # Configure streaming server

    target_ip = device["hostname"]
    serve_ip = streaming.get_serve_ip(target_ip)
    serv = streaming.start_server(serve_ip)

    files_urls = {}
    for key, path in files.items():
        r = serv.add_entry(key, path)
        files_urls.update(r)

    # Play the video through DLNA protocol

    print(files_urls)
    dlna.play(files_urls, device)


def run():

    parser = argparse.ArgumentParser(
        description="A minimal UPnP/DLNA media streamer.")
    parser.add_argument("-t", "--timeout", type=float, default=5)
    subparsers = parser.add_subparsers(dest="subparser_name")

    p_list = subparsers.add_parser('list')
    p_list.set_defaults(func=list_devices)

    p_play = subparsers.add_parser('play')
    p_play.add_argument("-d", "--device", dest="device_url")
    p_play.add_argument("-q", "--query-device", dest="device_query")
    p_play.add_argument("-s", "--subtitle", dest="file_subtitle")
    p_play.add_argument("-n", "--no-subtitle",
                        dest="use_subtitle", action="store_false")
    p_play.add_argument("file_video")
    p_play.set_defaults(func=play)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":

    run()
