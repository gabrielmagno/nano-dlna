#!/usr/bin/env python3
# encoding: UTF-8

import os
import socket
import threading

from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.python import log


def set_files(files, serve_ip, serve_port):

    files_index = { file_key : ( os.path.basename(file_path), 
                                 os.path.abspath(file_path),
                                 os.path.dirname(os.path.abspath(file_path)))
                             for file_key, file_path in files.items() }

    files_serve = { file_name : file_path 
                        for file_name, file_path, file_dir in files_index.values() }

    files_urls = { file_key : "http://{}:{}/{}/{}".format(serve_ip, serve_port, file_key, file_name) 
                       for file_key, (file_name, file_path, file_dir) in files_index.items() }

    return files_index, files_serve, files_urls


def start_server(files, serve_ip, serve_port=9000):

    import sys
    #log.startLogging(sys.stdout)

    files_index, files_serve, files_urls = set_files(files, serve_ip, serve_port)

    root = Resource()
    for file_key, (file_name, file_path, file_dir) in files_index.items():
        root.putChild(file_key.encode("utf-8"), Resource())
        root.children[file_key.encode("utf-8")].putChild(file_name.encode("utf-8"), File(file_path))

    reactor.listenTCP(serve_port, Site(root))
    threading.Thread(target=reactor.run, kwargs={"installSignalHandlers":False}).start()

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
    print(files)

    files_urls = start_server(files, "localhost")
    print(files_urls)

