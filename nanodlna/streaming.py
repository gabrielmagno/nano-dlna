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
            request.setResponseCode(500)

        @targetDeferred.addCallback
        def finish(_):
            request.finish()

        return NOT_DONE_YET


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self.root = Resource()

    def start(self):
        reactor.listenTCP(self.port, Site(self.root))
        server = threading.Thread(
            target=reactor.run, kwargs={"installSignalHandlers": False})
        server.start()

    def stop(self):
        if reactor.running:
            #reactor.callWhenRunning(reactor.stop)
            reactor.stop()

    def add_entry(self, key, path):
        self.root.putChild(key.encode("utf-8"), Resource())

        if os.path.exists(path):
            file_name = os.path.basename(path)
            entity = File(os.path.abspath(path))
        else:
            # assume we have a remote file
            parts = urllib.parse.urlparse(path)

            if parts.netloc == "www.youtube.com":
                v = pafy.new(path)
                match = v.getbest()

                file_name = v.videoid  # match.title
                entity = Proxy(match.url)
            else:
                file_name = parts.path[1:]  # remove initial '/'
                entity = Proxy(path)

        self.root.children[key.encode("utf-8")].putChild(
            file_name.encode("utf-8"), entity)

        return {key: "http://{0}:{1}/{2}/{3}".format(
            self.ip, self.port, key, file_name)}


def start_server(serve_ip, serve_port=9000):
    serv = Server(serve_ip, serve_port)
    serv.start()

    return serv


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

    serv = start_server("localhost")
    for key, path in files.items():
        r = serv.add_entry(key, path)
        print(r)

    print(serv.add_entry('haha', '/tmp'))
