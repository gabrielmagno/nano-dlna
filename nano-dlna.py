#!/usr/bin/env python3
# encoding: UTF-8

import socket
import http.server

SSDP_BROADCAST_PORT = 1900
SSDP_BROADCAST_ADDR = "239.255.255.250"

SSDP_BROADCAST_PARAMS = ["M-SEARCH * HTTP/1.1",
                         "HOST: {}:{}".format(SSDP_BROADCAST_ADDR,
                                              SSDP_BROADCAST_PORT),
                         "MAN: \"ssdp:discover\"",
                         "MX: 10",
                         "ST: ssdp:all", "", ""]
SSDP_BROADCAST_MSG = "\r\n".join(SSDP_BROADCAST_PARAMS)

class StreamingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    __version___ = "0.1"

    server_version = "StreamingHTTP/" + __version___

    def set_files(self, files=None, rename=False):
        self.files_ref = files
        self.files_index = {os.path.basename(file_path):file_path 
                                for (file_ref, file_path) in files.items()} 

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        ctype = self.guess_type(path)
        print(self.path, path, ctype)
        try:
            f = open(self.files_ref[path], "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        try:
            self.send_response(200)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise


def get_devices():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
    s.bind(("", SSDP_BROADCAST_PORT))
    
    s.sendto(bytes(SSDP_BROADCAST_MSG, "UTF-8"), (SSDP_BROADCAST_ADDR, 
                                                  SSDP_BROADCAST_PORT))
    
    devices = []

    while True:
        data, addr = s.recvfrom(1024)
        info = [a.split(":", 1) for a in data.decode("UTF-8").split("\r\n")[1:]]
        device = dict([(a[0].strip(), a[1].strip()) for a in info if len(a) >= 2])
        devices.append(device)
        print(info)

    return devices


def set_stream_server(http_port):
    files = {"file_cover": "/var/tmp/nano-dlna/imagem_mundo.jpg",
             "file_video": "/var/tmp/nano-dlna/video_evandro.mp4"}
    
    httph = StreamingHTTPRequestHandler
    httpd = http.server.HTTPServer(("", http_port), httph)
    httpd.RequestHandlerClass.set_files(files)
    
    print("HTTP server started: http://localhost:{}/".format(http_port))
    httpd.serve_forever()


def play():
    pass

set_stream_server(8000)

