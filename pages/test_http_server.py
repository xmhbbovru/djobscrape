#!/usr/bin/env python
""" Serve webpages to test dice_scrape.py.
    test_http_server.py rev 2013 Oct 02 by Stuart Ambler
    Copyright (c) 2013 Stuart Ambler.
    Distributed under the Boost License in the accompanying file LICENSE.
    Tested with Python 2.7.3.
    Usage: ./test_http_server.py  or  python -m testhttpserver .
    Run automatically by test_dice_scrape.
"""

from __future__ import print_function # for Python 2

import sys
import BaseHTTPServer
import CGIHTTPServer  # CGI for possible future use in fancier tests
import cgitb
cgitb.enable ()

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8000
init_server_address = ("", port)  # for localhost:port

server_class  = BaseHTTPServer.HTTPServer
handler_class = CGIHTTPServer.CGIHTTPRequestHandler
handler_class.protocol_version = "HTTP/1.1"  # 1.1 requires Content-length hdr
handler_class.cgi_directories  = ["/cgi-bin"]

httpd = server_class(init_server_address, handler_class)
server_address = httpd.socket.getsockname()
print("HTTP server with CGI; IP address", server_address[0],
      ", port", server_address[1])
httpd.serve_forever()
