import threading
import http.server
import os

class StreamingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def translate_path(self, path):
        if self.files_index is None:
            return super(StreamingHTTPRequestHandler, self).translate_path(path)
        else:
            return self.files_index.get(path, "")

HTTP_PORT_DEFAULT = 8000

http_port = HTTP_PORT_DEFAULT

files = {"file_cover": "/var/tmp/nano-dlna/cover.jpg",
         "file_video": "/var/tmp/nano-dlna/video_1.jpg",
         "file_subtitle": "/var/tmp/nano-dlna/video_1.srt"}
files_index = {"/{}".format(os.path.basename(file_path)):file_path 
                   for (file_ref, file_path) in files.items() } 

httph = StreamingHTTPRequestHandler
httph.files_index = files_index 

httpd = http.server.HTTPServer(("", http_port), httph)

thread_httpd = threading.Thread(target=httpd.serve_forever, args=[])

print("HTTP server started: http://localhost:{}/".format(http_port))
thread_httpd.start()


