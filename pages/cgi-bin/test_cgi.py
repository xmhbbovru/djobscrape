#!/usr/bin/env python
""" Serve webpages to test dice_scrape.py.
    test_cgi.py rev 2013 Oct 02 by Stuart Ambler
    Copyright (c) 2013 Stuart Ambler.
    Distributed under the Boost License in the accompanying file LICENSE.
    In browser address bar, enter http://127.0.0.1:8000/cgi-bin/test_cgi.py
    Tested with test_http_server.py under Python 2.7.3.
"""

from __future__ import print_function # for Python 2

content = ("<html><head><title>Test CGI</title></head>"
           + "<body><p>from CGI</p>"
           + "</body></html>")
content_length = len(content)
print("Content-length:", content_length, end="\r\n")
print("Content-type: text/html", end="\r\n\r\n")
print(content, end="")
