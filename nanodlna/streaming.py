#!/usr/bin/env python3
# encoding: UTF-8

import os
import socket
import threading
import urllib.parse

import pafy
import treq

from twisted.logger import Logger
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.static import File

# from twisted.python import log


class Proxy(Resource):
    _logger = Logger()

    def __init__(self, url):
        Resource.__init__(self)
        self._url = url

    def __repr__(self):
        return f"Proxy('{self._url}')"

    def getChild(self, path, request):
        return self

    def render_GET(self, request):
        targetDeferred = treq.get(self._url)

        @targetDeferred.addCallback
        def write(response):
            if response.code != 200:
                raise RuntimeError(response.code, "Failed to get response")
            for name, headers in response.headers.getAllRawHeaders():
                request.responseHeaders.setRawHeaders(name, list(headers))
            return response.collect(request.write)

        @targetDeferred.addErrback
        def fail(failure):
            # self._logger.failure(
            #     "Failed to request {url}",
            #     url=self._url,
            #     failure=failure,
            # )
            # print(failure)
            request.setResponseCode(500)

        @targetDeferred.addCallback
        def finish(ignored):
            request.finish()

        return NOT_DONE_YET


def start_server(files, serve_ip, serve_port=9000):
    files_urls = {}

    root = Resource()
    for file_key, file_path in files.items():
        root.putChild(file_key.encode("utf-8"), Resource())

        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            entity = File(os.path.abspath(file_path))
        else:
            # assume we have a remote file
            parts = urllib.parse.urlparse(file_path)

            if parts.netloc == "www.youtube.com":
                v = pafy.new(file_path)
                match = v.getbest()

                file_name = v.videoid  # match.title
                entity = Proxy(match.url)
            else:
                file_name = parts.path[1:]  # remove initial '/'
                entity = Proxy(file_path)

        root.children[file_key.encode("utf-8")].putChild(
            file_name.encode("utf-8"), entity)

        files_urls[file_key] = "http://{0}:{1}/{2}/{3}".format(
            serve_ip, serve_port, file_key, file_name)

    reactor.listenTCP(serve_port, Site(root))
    server = threading.Thread(
        target=reactor.run, kwargs={"installSignalHandlers": False})
    server.start()

    return files_urls


def stop_server():
    # TODO: what ... how ... ???
    # if reactor.running:
    #     #reactor.callWhenRunning(reactor.stop)
    #     reactor.stop()
    pass


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
    files['yt'] = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    print(files)

    files_urls = start_server(files, "localhost")
    print(files_urls)
