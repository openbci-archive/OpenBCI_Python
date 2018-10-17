#   Copyright 2014 Dan Krause
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import socket
import sys

pyVersion = sys.version_info[0]
if pyVersion == 2:
    # Imports for Python 2
    import httplib
    from StringIO import StringIO as SocketIO
else:
    # Imports for Python 3+
    import http.client
    from io import BytesIO as SocketIO


class SSDPResponse(object):
    class _FakeSocket(SocketIO):
        def makefile(self, *args, **kw):
            return self

    def __init__(self, response):

        if pyVersion == 2:
            r = httplib.HTTPResponse(self._FakeSocket(response))
        else:
            r = http.client.HTTPResponse(self._FakeSocket(response))

        r.begin()
        self.location = r.getheader("location")
        self.usn = r.getheader("usn")
        self.st = r.getheader("st")
        self.cache = r.getheader("cache-control").split("=")[1]

    def __repr__(self):
        return "<SSDPResponse({location}, {st}, {usn})>".format(**self.__dict__)


def discover(service, timeout=5, retries=1, mx=3, wifi_found_cb=None):
    group = ("239.255.255.250", 1900)
    message = "\r\n".join([
        'M-SEARCH * HTTP/1.1',
        'HOST: {0}:{1}',
        'MAN: "ssdp:discover"',
        'ST: {st}', 'MX: {mx}', '', ''])

    socket.setdefaulttimeout(timeout)
    responses = {}
    for _ in range(retries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sockMessage = message.format(*group, st=service, mx=mx)
        if pyVersion == 3:
            sockMessage = sockMessage.encode("utf-8")
        sock.sendto(sockMessage, group)
        while True:
            try:
                response = SSDPResponse(sock.recv(1024))
                if wifi_found_cb is not None:
                    wifi_found_cb(response)
                responses[response.location] = response
            except socket.timeout:
                break
    return list(responses.values())
