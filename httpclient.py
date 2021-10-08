#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        body = data.split("\r\n")
        code = int(body[0].split(" ")[1])
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        body = data.split("\r\n\r\n")
        return body[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def get_request_info(self,url):
        path="None"
        port="None"
        host="None"
        params="None"

        request_info = url.split(":")

        if(len(request_info) > 2):
            port = request_info[2].split("/")[0]
            host = request_info[1].replace("//", "")

            if("?" in request_info[2]):
                info = request_info[2].split("?")
                params = info[1]
                path = info[0].replace(port,"")

            else:
                path = request_info[2].replace(port,"")
            port = int(port)

        else:
            port = 80
            temp1 = request_info[1].replace("//", "")
            temp = temp1.split("/")
            host = temp[0]

            if("?" in request_info[1]):
                info = temp1.split("?")
                params = info[1]
                path = info[0].replace(host, "")
            else:
                path = temp1.replace(host, "")

        if(path==""):
            path="/"

        return(host, port, path, params)
        
    def GET(self, url, args=None):
        host, port, path, params = self.get_request_info(url)

        self.connect(host, port)

        request_line = "GET %s HTTP/1.1\r\n" % path
        host_header = "Host: %s\r\n" % host
        connection_header = "Connection: close\r\n"
        header_end = "\r\n"
    
        get_request = request_line+host_header+connection_header+header_end
        
        self.sendall(get_request)

        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        if(args!=None):
            for arg in args.keys():
                body = body+arg+"="+args[arg]+"&"

        self.get_request_info(url)
        host, port, path, params = self.get_request_info(url)

        request_line = "POST %s HTTP/1.1\r\n" % path
        host_header = "Host: %s\r\n" % host
        connection_header = "Connection: close\r\n"
        type_header = "Content-Type: application/x-www-form-urlencoded\r\n"

        if(args!=None):
            content_len = len(body)
        else:
            content_len = 0

        content_len_header = "Content-Length: %d\r\n" % content_len
        header_end = "\r\n"

        post_request = request_line+host_header+type_header+connection_header+content_len_header+header_end+body

        self.connect(host, port)

        self.sendall(post_request)

        response = self.recvall(self.socket)

        body = self.get_body(response)

        code = self.get_code(response)

        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
