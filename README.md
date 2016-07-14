nano-dlna
=========

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


List the available devices in my network:

    nanodlna list

```
Device 1:
{
    "location": "http://192.168.1.11:37904/MediaRenderer1.xml",
    "friendly_name": "32LV5500-SD",
    "action_url": "http://192.168.1.11:37904/upnp/control/AVTransport1",
    "hostname": "192.168.1.11",
    "st": "urn:schemas-upnp-org:service:AVTransport:1"
}


Device 2:
{
    "location": "http://192.168.1.13:1082/",
    "friendly_name": "osmc",
    "action_url": "http://192.168.1.13:1082/AVTransport/e8dcdde7-2c9f-75a6-7351-494522884cd2/control.xml",
    "hostname": "192.168.1.13",
    "st": "urn:schemas-upnp-org:service:AVTransport:1"
}
```

If your device is not being listed, you might need to increase the search timeout:

	nanodlna -t 20 list


### Play

Play a video, automatically loading the subtitles if available, selecting a random device:

    nanodlna play That.Movie.1989.1080p.BluRay.x264.HuE.mkv

Play a video, specifying the device through query (scan for devices before playing):

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

