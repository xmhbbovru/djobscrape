#!/usr/bin/env python
""" Runs dice_scrape.py testnojobnrs.html test, capturing output
    makecomparenojobnrs.py rev 2013 June 23, by Stuart Ambler.
    Copyright (c) 2013 Stuart Ambler.
    Distributed under the Boost License in the accompanying file LICENSE.
    Usage:  ./makecomparenojobnrs.py [all_fields]
    where [] denotes optional: if all_fields (case ignored) is present
    in the command line, dice_scrape_cfg.ALL_FIELDS is set True
    for dice_scrape; otherwise it is left at its default value, False.
    Tested with python 2.7.3.
"""

import re
import sys

all_fields_reo = re.compile ("ALL_FIELDS", re.I)

import dice_scrape_cfg
if len (sys.argv) >= 2:
    mob = all_fields_reo.search (sys.argv[1])
    if mob is not None:
        dice_scrape_cfg.ALL_FIELDS = True
import dice_scrape

# sys.argv[0] has the path too, but it doesn't matter for this purpose
main_args = ["./dice_scrape.py",
             "http://localhost:8000/testnojobnrs.html", "test"]
dice_scrape.main_func (main_args)
