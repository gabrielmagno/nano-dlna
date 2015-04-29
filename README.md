# nano-dlna
A minimal UPnP/DLNA media streamer

## Usage
node index.js --folder="/folder/to/files" --file_video="video.mkv" --file_sub="video.srt" --media-renderer-url="http://192.168.1.13:1577/"

##TODO
- [X] HTTP server to stream the media files.
- [ ] Multi-folder file streaming
- [ ] Automatic find video and subtitle files
- [X] MediaRenderer client connection
- [X] Send metadata of the video to the MediaRenderer
- [ ] Handle flexible metadata
- [ ] SDDP search to find UPnP devices
- [X] Argument parsing
- [ ] CLI interface to send controller actions (play, pause, stop, etc) to the MediaRenderer
- [ ] CLI progress bar visualization
