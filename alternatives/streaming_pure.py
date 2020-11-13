#!/usr/bin/env python3
# encoding: UTF-8

import http.server
import os
import re
import socket
import threading
from http import HTTPStatus


class StreamingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    __version___ = "1.0"

    protocol_version = 'HTTP/1.1'

    server_version = "StreamingHTTP/" + __version___

    # timeout = 10
    # timeout = 2

    buffer_size = 2 * 1024 * 1024

    def set_files(files):
        files_index = {file_key: (os.path.basename(file_path),
                                  os.path.abspath(file_path))
                       for file_key, file_path in files.items()}
        files_serve = {file_name: file_path
                       for file_name, file_path in files_index.values()}
        return files_index, files_serve

    def do_GET(self):
        f, start_range, end_range = self.send_head()
        if f:
            try:
                f.seek(start_range, 0)
                size = end_range - start_range + 1

                # buf = f.read(size)
                # sent = self.wfile.write(buf)

                # TODO: improve buffered reading (it is slower than full
                # reading)
                while size > 0:
                    buf = f.read(min(self.buffer_size, size))
                    size -= len(buf)
                    if not buf:
                        break
                    self.wfile.write(buf)

            finally:
                f.close()

    def do_HEAD(self):
        f, start_range, end_range = self.send_head()
        if f:
            f.close()

    def send_head(self):
        file_name = self.path[1:]
        ctype = self.guess_type(file_name)
        f = None

        try:
            file_path = self.files_serve[file_name]
            f = open(file_path, 'rb')
        except Exception:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return (None, 0, 0)

        try:
            fs = os.fstat(f.fileno())
            size_full = fs[6]

            if "Range" in self.headers:
                range_value = re.search(r"bytes=(?P<start>\d+)?-(?P<end>\d+)?",
                                        self.headers["Range"])
                start_range = max(int(range_value.group("start") or 0), 0)
                end_range = min(int(range_value.group("end")
                                    or (size_full - 1)), (size_full - 1))
                size_partial = end_range - start_range + 1
                assert size_partial > 0

                self.send_response(HTTPStatus.PARTIAL_CONTENT)
                self.send_header(
                    "Content-Range",
                    "bytes "
                    "{0}-{1}/{2}".format(start_range, end_range, size_full))

            else:
                start_range = 0
                end_range = size_full - 1
                size_partial = size_full

                self.send_response(HTTPStatus.OK)

            self.send_header("Accept-Ranges", "bytes")
            # self.send_header("Cache-Control", "public, max-age=0")
            self.send_header(
                "Last-Modified", self.date_time_string(fs.st_mtime))
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(size_partial))
            self.send_header("Connection", "close")
            self.end_headers()
            return (f, start_range, end_range)
        except Exception:
            f.close()
            raise


def start_server(files, serve_ip, serve_port=9000):

    httph = StreamingHTTPRequestHandler
    httph_files = StreamingHTTPRequestHandler.set_files(files)
    httph.files_index, httph.files_serve = httph_files

    httpd = http.server.HTTPServer((serve_ip, serve_port), httph)
    threading.Thread(target=httpd.serve_forever).start()

    files_urls = {
        file_key: "http://{0}:{1}/{2}".format(serve_ip, serve_port, file_name)
        for file_key, (file_name, file_path) in httph.files_index.items()}

    return files_urls


def get_serve_ip(target_ip, target_port=80):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((target_ip, target_port))
    serve_ip = s.getsockname()[0]
    s.close()
    return serve_ip


if __name__ == "__main__":

    import sys

    files = {"file_{0}".format(i): file_path for i,
             file_path in enumerate(sys.argv[1:], 1)}

    start_server(files, "localhost")
