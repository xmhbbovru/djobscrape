""" Tests dice_scrape.py.
    testpytestnotall.py rev 2013 June 23, by Stuart Ambler.
    Copyright (c) 2013 Stuart Ambler.
    Distributed under the Boost License in the accompanying file LICENSE.
    Usage:  python -m py.test testpytestnotall.py
    The difference from testpytest.py is that this one doesn't set ALL_FIELDS
    Tested with python 2.7.3 nd pytest 2.3.5.
"""

import os
import signal
from subprocess import Popen
from time import sleep
import pytest

import dice_scrape_cfg
import dice_scrape

class TestDiceScrape:
    fnull = None
    server_popen = None
    @classmethod
    def setup_class (cls):
        """ Setup for execution of tests.
        Args: class cls
        Returns: nothing
        """
        TestDiceScrape.fnull = open (os.devnull, "w")
        TestDiceScrape.server_popen = Popen ("cd pages; ./test_http_server.py",
                                             shell=True,
                                             stdout=TestDiceScrape.fnull,
                                             preexec_fn=os.setsid)
        sleep (1)  # need server to start running before run tests

    @classmethod
    def teardown_class (cls):
        """ Teardown after execution of tests.
        Args: class cls
        Returns: nothing
        """
        os.killpg (TestDiceScrape.server_popen.pid, signal.SIGTERM)
        TestDiceScrape.fnull.close ()

    def compareouterr (self, capsys, outfilename, errfilename):
        """ Compares out, err from capsys with contents of files.
        Args: outfilename, errfilename filenames of correct stdout, stderr.
        Returns: True if compares ok, False otherwise
        """
        out, err = capsys.readouterr ()
        outf = open (outfilename)
        outcorrect = outf.read ()
        outf.close ()
        errf = open (errfilename)
        errcorrect = errf.read ()
        errf.close ()
        return out == outcorrect and err == errcorrect

    def testhtml (self, capsys):
        main_args = ["./dice_scrape.py",
                     "http://localhost:8000/test.html", "test"]
        dice_scrape.main_func (main_args)
        assert self.compareouterr (capsys,
                                   "testoutnotall",
                                   "testerrnotall")
        
    def testhtmlnojobnrs (self, capsys):
        main_args = ["./dice_scrape.py",
                     "http://localhost:8000/testnojobnrs.html", "test"]
        dice_scrape.main_func (main_args)
        assert self.compareouterr (capsys,
                                   "testoutnojobnrsnotall",
                                   "testerrnojobnrsnotall")

    def testnonexistent (self, capsys):
        main_args = ["./dice_scrape.py",
                     "http://localhost:8000/testnonexistent.html", "test"]
        dice_scrape.main_func (main_args)
        assert self.compareouterr (capsys,
                                   "testoutnonexistentnotall",
                                   "testerrnonexistentnotall")
