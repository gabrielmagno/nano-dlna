#!/usr/bin/env python3
# encoding: UTF-8

import os
import http.server
from http import HTTPStatus
import re

class StreamingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    __version___ = "0.1"

    server_version = "StreamingHTTP/" + __version___

    def set_files(files):
        files_index = { os.path.basename(file_path) : 
                             os.path.abspath(file_path)
                                 for file_path in files }
        print(files_index)
        return files_index

    def do_GET(self):
        f, start_range, end_range = self.send_head()
        if f:
            try:
                f.seek(start_range, 0)
                size = end_range - start_range + 1
                data = f.read(size)
                self.wfile.write(data)
            finally:
                f.close()

    def send_head(self):
        file_key = self.path[1:] 
        ctype = self.guess_type(file_key)
        f = None

        try:
            file_path = self.files_index[file_key] 
            f = open(file_path, 'rb')
        except:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return (None, 0, 0)
        
        try:
            fs = os.fstat(f.fileno())
            size_full = fs[6] 

            if "Range" in self.headers:
                #TODO: test cases
                range_value = re.search("bytes=(?P<start>\d+)?-(?P<end>\d+)?", 
                                        self.headers["Range"])
                start_range = int(range_value.group("start") or 0)
                end_range = int(range_value.group("end") or (size_full - 1))
                size_partial = end_range - start_range + 1
                assert size_partial > 0

                self.send_response(HTTPStatus.PARTIAL_CONTENT)
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Range", 
                                 "bytes {}-{}/{}".format(start_range, end_range, size_full))

            else:
                start_range = 0
                end_range = size_full - 1
                size_partial = size_full

                self.send_response(HTTPStatus.OK)
 
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(size_partial))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return (f, start_range, end_range)
        except:
            f.close()
            raise


if __name__ == "__main__":

    import sys

    HTTP_PORT = 9999

    files = sys.argv[1:]

    httph = StreamingHTTPRequestHandler

    httpd = http.server.HTTPServer(("", HTTP_PORT), httph)
    httpd.RequestHandlerClass.files_index = StreamingHTTPRequestHandler.set_files(files)
    httpd.serve_forever()

