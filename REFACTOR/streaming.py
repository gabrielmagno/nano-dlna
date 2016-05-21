#!/usr/bin/env python3
# encoding: UTF-8

import os
import http.server
from http import HTTPStatus
import socket
import re
import threading

def copyfileobj(fsrc, fdst, length=16*1024):
    """copy data from file-like object fsrc to file-like object fdst"""
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)


class StreamingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    __version___ = "0.1"

    protocol_version = 'HTTP/1.1'

    server_version = "StreamingHTTP/" + __version___


    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.

        """
        try:
            print("Esperando...")	
            self.raw_requestline = self.rfile.readline(65537)
            print("LIDO: {}\n\n".format(self.raw_requestline))	
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(
                    HTTPStatus.NOT_IMPLEMENTED,
                    "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            method()
            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout as e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return

    def handle(self):
        """Handle multiple requests if necessary."""
        self.close_connection = True

        self.handle_one_request()
        while not self.close_connection:
            self.handle_one_request()




    def set_files(files):
        files_index = { file_key : ( os.path.basename(file_path), 
                                     os.path.abspath(file_path)  )
                                 for file_key, file_path in files.items() }
        files_serve = { file_name : file_path 
                            for file_name, file_path in files_index.values() }
        return files_index, files_serve


    def do_GET(self):
        f, start_range, end_range = self.send_head()
        print("Range: {} - {} / {}".format(start_range, end_range, (end_range - start_range + 1)))
        if f:
            try:
                f.seek(start_range, 0)
                size = end_range - start_range + 1

                buf = f.read(size)
                print("Leu {}".format(len(buf)))
                sent = self.wfile.write(buf)
                print("Enviou {}".format(sent))

                ## TODO: buffered reading
                #self.wfile.flush()
                #total = 0
                #size_total = size
                #while size > 0:
                #    buf = f.read(min(65551, size))
                #    total += len(buf)
                #    print("read {}, total {}, size {} ({:.1f}%)".format(len(buf), total, size, 100*(total/size_total)))
                #    if not buf:
                #        break
                #    size -= len(buf)
                #    self.wfile.write(buf)
                #    self.wfile.flush()
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
        except:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return (None, 0, 0)
        
        try:
            fs = os.fstat(f.fileno())
            size_full = fs[6] 

            if "Range" in self.headers:
                range_value = re.search("bytes=(?P<start>\d+)?-(?P<end>\d+)?", 
                                        self.headers["Range"])
                start_range = max(int(range_value.group("start") or 0), 0)
                end_range = min(int(range_value.group("end") or (size_full - 1)), (size_full -1))
                size_partial = end_range - start_range + 1
                assert size_partial > 0

                self.send_response(HTTPStatus.PARTIAL_CONTENT)
                self.send_header("Content-Range", 
                                 "bytes {}-{}/{}".format(start_range, end_range, size_full))

            else:
                start_range = 0
                end_range = size_full - 1
                size_partial = size_full

                self.send_response(HTTPStatus.OK)
 
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "public, max-age=0")
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(size_partial))
            self.close_connection = True
            #self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.flush()
            return (f, start_range, end_range)
        except:
            f.close()
            raise


def start_server(files, serve_ip, serve_port=9000):

    httph = StreamingHTTPRequestHandler
    httph.files_index, httph.files_serve = StreamingHTTPRequestHandler.set_files(files)

    httpd = http.server.HTTPServer((serve_ip, serve_port), httph)
    threading.Thread(target=httpd.serve_forever).start()

    files_urls = { file_key : "http://{}:{}/{}".format(serve_ip, serve_port, file_name) 
                       for file_key, (file_name, file_path) in httph.files_index.items() }

    return files_urls


def get_serve_ip(target_ip, target_port=80):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((target_ip, target_port))
    serve_ip = s.getsockname()[0]
    s.close()
    return serve_ip


if __name__ == "__main__":

    import sys

    files = {"file_{}".format(i) : file_path  for i, file_path in enumerate(sys.argv[1:], 1)} 

    start_server(files, "localhost")

