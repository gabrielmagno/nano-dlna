#!/usr/bin/env python3

from __future__ import print_function

import argparse
import json
import os
import sys
import signal
import datetime
import tempfile

from . import devices, dlna, streaming

import logging


def set_logs(args):

    log_filename = os.path.join(
        tempfile.mkdtemp(),
        "nanodlna-{}.log".format(
            datetime.datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
        )
    )

    logging.basicConfig(
        filename=log_filename,
        filemode="w",
        level=logging.INFO,
        format="[ %(asctime)s ] %(levelname)s : %(message)s"
    )

    if args.debug_activated:
        logging.getLogger().setLevel(logging.DEBUG)

    print("nano-dlna log will be saved here: {}".format(log_filename))


def get_subtitle(file_video):

    video, extension = os.path.splitext(file_video)

    file_subtitle = "{0}.srt".format(video)

    if not os.path.exists(file_subtitle):
        return None
    return file_subtitle


def list_devices(args):

    set_logs(args)

    logging.info("Scanning devices...")
    my_devices = devices.get_devices(args.timeout, args.local_host)
    logging.info("Number of devices found: {}".format(len(my_devices)))

    for i, device in enumerate(my_devices, 1):
        print("Device {0}:\n{1}\n\n".format(i, json.dumps(device, indent=4)))


def find_device(args):

    logging.info("Selecting device to play")

    device = None

    if args.device_url:
        logging.info("Select device by URL")
        device = devices.register_device(args.device_url)
    else:
        my_devices = devices.get_devices(args.timeout, args.local_host)

        if len(my_devices) > 0:
            if args.device_query:
                logging.info("Select device by query")
                device = [
                    device for device in my_devices
                    if args.device_query.lower() in str(device).lower()][0]
            else:
                logging.info("Select first device")
                device = my_devices[0]

    return device


def play(args):

    set_logs(args)

    logging.info("Starting to play")

    # Get video and subtitle file names

    files = {"file_video": args.file_video}

    if args.use_subtitle:

        if not args.file_subtitle:
            args.file_subtitle = get_subtitle(args.file_video)

        if args.file_subtitle:
            files["file_subtitle"] = args.file_subtitle

    logging.info("Media files: {}".format(json.dumps(files)))

    device = find_device(args)
    if not device:
        sys.exit("No devices found.")

    logging.info("Device selected: {}".format(json.dumps(device)))

    # Configure streaming server
    logging.info("Configuring streaming server")

    target_ip = device["hostname"]
    if args.local_host:
        serve_ip = args.local_host
    else:
        serve_ip = streaming.get_serve_ip(target_ip)
    files_urls = streaming.start_server(files, serve_ip)

    logging.info("Streaming server ready")

    # Register handler if interrupt signal is received
    signal.signal(signal.SIGINT, build_handler_stop(device))

    # Play the video through DLNA protocol
    logging.info("Sending play command")
    dlna.play(files_urls, device)


def seek(args):
    set_logs(args)
    logging.info("Starting to seek")

    device = find_device(args)
    if not device:
        sys.exit("No devices found.")

    logging.info("Sending seek command")
    dlna.seek(args.target, device)


def build_handler_stop(device):
    def signal_handler(sig, frame):

        logging.info("Interrupt signal detected")

        logging.info("Sending stop command to render device")
        dlna.stop(device)

        logging.info("Stopping streaming server")
        streaming.stop_server()

        sys.exit(
            "Interrupt signal detected. "
            "Sent stop command to render device and "
            "stopped streaming. "
            "nano-dlna will exit now!"
        )
    return signal_handler


def pause(args):

    set_logs(args)

    logging.info("Selecting device to pause")
    device = find_device(args)

    # Pause through DLNA protocol
    logging.info("Sending pause command")
    dlna.pause(device)


def stop(args):

    set_logs(args)

    logging.info("Selecting device to stop")
    device = find_device(args)

    # Stop through DLNA protocol
    logging.info("Sending stop command")
    dlna.stop(device)


def run():

    parser = argparse.ArgumentParser(
        description="A minimal UPnP/DLNA media streamer.")
    parser.set_defaults(func=lambda args: parser.print_help())
    parser.add_argument("-H", "--host", dest="local_host")
    parser.add_argument("-t", "--timeout", type=float, default=5)
    parser.add_argument("-b", "--debug",
                        dest="debug_activated", action="store_true")
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

    p_seek = subparsers.add_parser('seek')
    p_seek.add_argument("-d", "--device", dest="device_url")
    p_seek.add_argument("-q", "--query-device", dest="device_query")
    p_seek.add_argument("target", help="e.g. '00:17:25'")
    p_seek.set_defaults(func=seek)

    p_pause = subparsers.add_parser('pause')
    p_pause.add_argument("-d", "--device", dest="device_url")
    p_pause.add_argument("-q", "--query-device", dest="device_query")
    p_pause.set_defaults(func=pause)

    p_stop = subparsers.add_parser('stop')
    p_stop.add_argument("-d", "--device", dest="device_url")
    p_stop.add_argument("-q", "--query-device", dest="device_query")
    p_stop.set_defaults(func=stop)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":

    run()
