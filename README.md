nano-dlna
=========

A minimal UPnP/DLNA media streamer.


Usage
-----

    nanodlna play That.Movie.1989.1080p.BluRay.x264.HuE.mkv


Features
--------
- Searching available DLNA devices in the local network
- Streaming audio
- Streaming video, with subtitle support


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
3. Filter only devices that provide UPnP's AVTransport service ()[http://www.upnp.org/specs/av/UPnP-av-AVTransport-v3-Service-20101231.pdf].


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

