#!/usr/bin/env python
""" Makes comparison files used as correct output by test dice_scrape.py.
    makecompareall.py rev 2013 June 22, by Stuart Ambler.
    Copyright (c) 2013 Stuart Ambler.
    Distributed under the Boost License in the accompanying file LICENSE.
    Usage:  python -m makecompareall.py
    Tested with python 2.7.3.
"""

import os
import re
import signal
import sys
from subprocess import Popen, call
from time import sleep

foutnull     = None
ferrnull     = None
server_popen = None

def setup ():
    """ Setup.
    Args: none
    Returns: nothing
    """
    global foutnull, ferrnull, server_popen
    foutnull = open (os.devnull, "w")
    ferrnull = open (os.devnull, "w")
    server_popen = Popen ("cd pages; ./test_http_server.py",
                          shell=True, stdout=foutnull, stderr=ferrnull,
                          preexec_fn=os.setsid)
    sleep (1)  # need server to start running before running scripts
    
def teardown ():
    """ Teardown.
    Args: none
    Returns: nothing
    """
    os.killpg (server_popen.pid, signal.SIGTERM)
    ferrnull.close ()
    foutnull.close ()
    
def main ():
    setup ()

    # run with all_fields set, then without that but with notall filename suffix

    all = [(" all_fields", ""), ("", "notall")]

    for tup in all:
        fout = open ("testout" + tup[1], "w")
        ferr = open ("testerr" + tup[1], "w")
        exit_code = call ("./makecompare.py" + tup[0],
                          shell=True, stdout = fout, stderr = ferr)
        if exit_code != 0:
            sys.stderr.write ("error generating test*\n")
            sys.stderr.flush ()
            fout.close ()
            ferr.close ()
        
        fout = open ("testoutnojobnrs" + tup[1], "w")
        ferr = open ("testerrnojobnrs" + tup[1], "w")
        exit_code = call ("./makecomparenojobnrs.py" + tup[0],
                          shell=True, stdout = fout, stderr = ferr)
        if exit_code != 0:
            sys.stderr.write ("error generating test*\n")
            sys.stderr.flush ()
            fout.close ()
            ferr.close ()
        
        fout = open ("testoutnonexistent" + tup[1], "w")
        ferr = open ("testerrnonexistent" + tup[1], "w")
        exit_code = call ("./makecomparenonexistent.py" + tup[0],
                          shell=True, stdout = fout, stderr = ferr)
        if exit_code != 0:
            sys.stderr.write ("error generating test*\n")
            sys.stderr.flush ()
            fout.close ()
            ferr.close ()
        
    teardown ()

if __name__ == "__main__":
    main ()
