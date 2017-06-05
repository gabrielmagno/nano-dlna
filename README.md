nano-dlna
=========

[![Build Status](https://travis-ci.org/gabrielmagno/nano-dlna.svg?branch=master)](https://travis-ci.org/gabrielmagno/nano-dlna)
[![PyPI](https://img.shields.io/pypi/v/nanodlna.svg)](https://pypi.python.org/pypi/nanodlna)
[![License](https://img.shields.io/github/license/gabrielmagno/nano-dlna.svg)](https://github.com/gabrielmagno/nano-dlna/blob/master/LICENSE)

A minimal UPnP/DLNA media streamer.

nano-dlna is a command line tool that allows you to play a local video file in your TV (or any other DLNA compatible device).


Features
--------
- Searching available DLNA devices in the local network
- Streaming audio
- Streaming video, with subtitle support


Usage
-----

### List

Scan compatible devices and list the available ones:

    nanodlna list

If your device is not being listed, you might need to increase the search timeout:

    nanodlna -t 20 list


### Play

Play a video, automatically loading the subtitles if available, selecting a random device:

    nanodlna play That.Movie.mkv

Play a video, specifying the device through query (scan devices before playing):

    nanodlna play That.Movie.mkv -q "osmc"

Play a video, specifying the device through its exact location (no scan, faster):

    nanodlna play That.Movie.mkv -d "http://192.168.1.13:1082/"



Installation
------------

nano-dlna can be installed as a regular python module by running:

    $ [sudo] pip install nanodlna


Technical Details
-----------------

nano-dlna is basically a one-file DLNA MediaServer and a self DLNA MediaController.

How does `list` work?

1. Issue an SSDP M-Search broadcast message in the network
2. Capture the responses and register the devices
3. Filter only devices that provide [UPnP's AVTransport service](http://www.upnp.org/specs/av/UPnP-av-AVTransport-v3-Service-20101231.pdf)


How does `play` work?

1. Setup an HTTP server to provide the media files to be streamed (including subtitles)
2. Send a `SetAVTransportURI` message to the device, specifying the HTTP URLs of the media files
3. Send a `Play` message to the device


TODO
----
- [ ] Documentation
- [ ] CLI interface to send controller actions (play, pause, stop, etc) to the MediaRenderer
- [ ] CLI progress bar visualization
- [ ] Playlist

