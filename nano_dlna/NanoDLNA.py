import http.server
import os

class StreamingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    __version___ = "0.1"

    server_version = "StreamingHTTP/" + __version___

    def set_files(self, files=None, rename=False):
        self.files_ref = files
        self.files_index = {os.path.basename(file_path):file_path for (file_ref, file_path) in files.items()} 

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



HTTP_PORT_DEFAULT = 8000

http_port = HTTP_PORT_DEFAULT

files = {"file_cover": "/var/tmp/nano-dlna/imagem_mundo.jpg",
         "file_video": "/var/tmp/nano-dlna/video_evandro.mp4"}

httph = StreamingHTTPRequestHandler
httph.set_files(files)
httpd = http.server.HTTPServer(("", http_port), httph)

print("HTTP server started: http://localhost:{}/".format(http_port))
httpd.serve_forever()

