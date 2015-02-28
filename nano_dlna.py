import http.server
import os

class StreamingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    server_version = "StreamingHTTP/0.1"

    def translate_path(self, path):
        if self.files_index is None:
            return super(StreamingHTTPRequestHandler, self).translate_path(path)
        else:
            return self.files_index.get(path, "")

HTTP_PORT_DEFAULT = 8000

http_port = HTTP_PORT_DEFAULT

files = {"file_cover": "/dados/Videos/Series/Seinfeld/cover.jpg",
         "file_video": "/dados/Videos/Series/Seinfeld/Pilot - [DVD]/001 - The Seinfeld Chronicles - [DVD].avi",
         "file_subtitle": "/dados/Videos/Series/Seinfeld/Pilot - [DVD]/001 - The Seinfeld Chronicles - [DVD].srt"}

httph = StreamingHTTPRequestHandler
httph.files_index = {"/{}".format(os.path.basename(file_path)):file_path 
                         for (file_ref, file_path) in files.items() } 

httpd = http.server.HTTPServer(("", http_port), httph)

print("HTTP server started: http://localhost:{}/".format(http_port))
httpd.serve_forever()

