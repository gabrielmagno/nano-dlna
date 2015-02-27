import http.server

HTTP_PORT_DEFAULT = 8000

http_port = HTTP_PORT_DEFAULT

httpd = http.server.HTTPServer(("", http_port), http.server.SimpleHTTPRequestHandler)

print("HTTP server started: http://localhost:{}/".format(http_port))
httpd.serve_forever()

