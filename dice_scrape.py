#!/usr/bin/python
""" Scrapes selected Dice jobs.  
dice_scrape.py v4 rev 2013 June 23 by Stuart Ambler (v3 was test update only).
Copyright (c) 2013 Stuart Ambler.
Distributed under the Boost License in the accompanying file LICENSE.
Usage: python dice_scrape.py "search term"
or     python dice_scrape.py "search term" title
to require that the search term be found in the title, for Dice's option to
search title only, or
       python dice_scrape.py "test_url" test
for test with e.g. what's in the pages subdirectory: test_http_server,
test_url=http://localhost:8000/test.html or testnojobnrs, and any pages
 they link to, such as job*.html.
stdout: comma separated quoted string values, one line per job:
position_id, dice_id, position, taxterm, length, areacode, removed.
stderr: is used for informational as well as error messages.
Tested with Python 2.7.3.  There's incomplete provision for Python 3;
e.g., issues of byte vs. string patterns for re need to be resolved.
"""

from __future__ import print_function # for Python 2

import httplib
import re
import sys
from time import sleep
#try:  # for Python 3
#    from urllib.request import urlopen
#    from urllib.error import HTTPError, URLError
#    from urllib.parse import urlencode
#except ImportError: # for Python 2; indent the following if uncomment
from urllib2 import urlopen
from urllib2 import HTTPError, URLError
from urllib import urlencode
import xml.sax.saxutils

import dice_scrape_cfg

# Regular expressions (strings) and their compilation into regular expression
# objects are global so they will be compiled only once.

# Used by fix_up_url:

HTTP_STR = r'http://'
HTTP_REO = re.compile (HTTP_STR, re.I)
DICE_STR = r'www.dice.com'
DICE_REO = re.compile (DICE_STR, re.I)
AMP_STR  = r'&amp;'
AMP_REO  = re.compile (AMP_STR,  re.I)

# Used by process:

LINK_POSITION_STR = (r'<tr\s+class\s*=\s*"[^"]+">\s*<td>\s*<div>\s*<a\s+href'
                     r'\s*=\s*"(?P<link>[^"]+)"[^>]*>(?P<position>[^<]*)</a>')
LINK_POSITION_REO = re.compile (LINK_POSITION_STR, re.I)

COMPANY_STR = (r'<a\s+href\s*=\s*"/jobsearch/company/[^"]+"\s+title\s*=\s*'
               r'"[^"]*"[^>]*>(?P<company>[^<]+)</a>')

LINK_POSITION_OR_COMPANY_STR = (LINK_POSITION_STR + r'|' + COMPANY_STR)
LINK_POSITION_OR_COMPANY_REO = re.compile (LINK_POSITION_OR_COMPANY_STR, re.I)

# Used by get_job_nrs:

JOB_NRS_STR  = (r'<h2>\s*Search results:\s*(\d+)\s*-\s*(\d+)\s*of\s*(\d+)\s*'
                r'</h2>')
JOB_NRS_REO  = re.compile (JOB_NRS_STR,   re.I)

# Used by process_detail:

# More fields are available to be scraped and output than are processed
# at present.  Company is scraped though not output, to avoid commenting logic.

# Dice apparently has custom job pages depending on employer.  Different
# labels are used for the same information.  As more job pages are examined,
# no doubt additional alternatives will need to be added to the following.

# <span>, </span> were only used by Yoh in the sample examined.  It might be
# a good idea to use BeautifulSoup to parse the html, for robustness in the
# face of this sort of thing and perhaps for performance; but I don't know
# what the limits might be to the variations, or at what point BeautifulSoup
# might perform better than the current method.  Or, maybe it would be better
# to use Lynx and just operate on text.

# Collabera sometimes had white space between labels and the following colons.

# Most listings had colons after the labels, but one from CompuCom didn't;
# it also used "Job Status" as a general type of job, with Tax Term as we
# take it, and used "Job ID" for what we call position.  Also it switched
# the usual use of <dt> and <dd>.

MAYBE_MORE_CLOSE = r'(?:\s+[^>]*)?>'
DT               = r'<(?P<dt>dt|dd|td)' + MAYBE_MORE_CLOSE
CLOSE_DT         = r'</(?P=dt)>'
DD               = r'<(?P<dd>dd|dt|td)' + MAYBE_MORE_CLOSE
CLOSE_DD         = r'</(?P=dd)>'
MAYBE_SPAN_DATA  = (  r'(?P<span><span' + MAYBE_MORE_CLOSE
                    + r')?(?P<data>.+)(?(span)</span>)')

# The following global variables used only during import or execution as a
# script, and in process_detail; and are only modified during import or
# execution as a script.  They're named as constants because of this.

REO_LIST          = []  # regular expression objects to search for fields
LAST_REO_IX       = 0
REO_IX_DICT       = {}  # indices into REO_LIST
PRINT_REO_IX_LIST = []  # indices into REO_LIST, field_list of items to print

for (label, name, read, write, special, order) in dice_scrape_cfg.FIELD_LIST:
    if not read and not dice_scrape_cfg.ALL_FIELDS:
        continue
    if special:
        if   name == "position":
            REO_LIST.append (re.compile (label, re.I))
        elif name == "removed":
            REO_LIST.append (re.compile (label, re.I))
    else:
        REO_LIST.append (re.compile (           DT + label           + CLOSE_DT
                                     + r'\s*' + DD + MAYBE_SPAN_DATA + CLOSE_DD,
                                     re.I))
    REO_IX_DICT[name] = LAST_REO_IX
    if write or dice_scrape_cfg.ALL_FIELDS:
        PRINT_REO_IX_LIST.append ((LAST_REO_IX, order))
    LAST_REO_IX += 1
    PRINT_REO_IX_LIST.sort (key=lambda t: t[1])

APPLY_DICE_ID_STR     = (r'<a\s+id\s*=\s*"APPLY_FOR_JOB.{0,2}"\s+href\s*=\s*".*'
                         r'&amp;diceid=(?P<dice_id>[^&">]+)')
APPLY_DICE_ID_REO     = re.compile (APPLY_DICE_ID_STR, re.I)
APPLY_POSITION_ID_STR = (r'<a\s+id\s*=\s*"APPLY_FOR_JOB.{0,2}"\s+href\s*=\s*".*'
                         r'&amp;(?:jobid|positionid)=(?P<position_id>[^&">]+)')
APPLY_POSITION_ID_REO = re.compile (APPLY_POSITION_ID_STR, re.I)

JS_DICE_ID_STR        = (r'var\s+joinNetworkHref\s*=\s*"/jobsearch/servlet/'
                         r'JobSearch.*&diceID=(?P<dice_id>[^&"]+)')
JS_DICE_ID_REO        = re.compile (JS_DICE_ID_STR, re.I)

BOLD_STR              = r'(</?b' + MAYBE_MORE_CLOSE + r')'
BOLD_REO              = re.compile (BOLD_STR, re.I)
A_STR                 = r'(</?a' + MAYBE_MORE_CLOSE + r')'
A_REO                 = re.compile (A_STR, re.I)


def process_removed (field_list):
    """Additionally process 'removed'.
    Args: field_list of values retrieved so far.
    Returns: bool removed (side effect updates a value in field_list).
    """
    field_list[REO_IX_DICT["removed"]]  = ("True"
                                     if field_list[REO_IX_DICT["removed"]] != ""
                                     else "False")
    return (field_list[REO_IX_DICT["removed"]] == "True")


def process_position (field_list, position):
    """Look in additional place for position.
    Args: field_list of values retrieved so far, position to use.
    Returns: nothing (side effect updates a value in field_list).
    """
    field_list[REO_IX_DICT["position"]] = position


def process_company (field_list, company):
    """Look in additional place for company.
    Args: field_list of values retrieved so far, company to use if no other.
    Returns: nothing (side effect updates a value in field_list).
    """
    if field_list[REO_IX_DICT["company"]] == "":
        field_list[REO_IX_DICT["company"]] = company


def process_dice_id (detail, field_list):
    """Look in additional places for Dice ID.
    Args: job detail page, field_list of values retrieved so far.
    Returns: bool successfully found Dice ID (side effect updates a value
             in field_list).
    """
    if field_list[REO_IX_DICT["dice_id"]] == "":
        mob = APPLY_DICE_ID_REO.search (detail)
        if mob is None:
            mob = JS_DICE_ID_REO.search (detail)
            if mob is None:
                return False
            else:
                field_list[REO_IX_DICT["dice_id"]] = mob.group ('dice_id')
        else:
            field_list[REO_IX_DICT["dice_id"]] = mob.group ('dice_id')
    return True


def process_position_id (detail, field_list):
    """Look in additional place for position ID.
    Args: job detail page, field_list of values retrieved so far.
    Returns: nothing (side effect updates a value in field_list).
    """
    if field_list[REO_IX_DICT["position_id"]] == "":
        mob = APPLY_POSITION_ID_REO.search (detail)
        if mob is not None:
            field_list[REO_IX_DICT["position_id"]] = mob.group ('position_id')


def process_detail (detail, position, company):
    """ Scrape data from job detail page.
    Args: detail page, job list page position, company (last two may be blank).
    Returns: bool has Dice ID, bool job removed from database.
    """
    field_list = []  # retrieved values
    for reo in REO_LIST:
        mob = reo.search (detail)
        if mob is None:
            field_list.append ("")
        else:
            field_list.append (mob.group ('data'))

    removed = process_removed (field_list)
    process_position (field_list, position)
    process_company (field_list, company)
    if not process_dice_id (detail, field_list):
        return False, removed
    process_position_id (detail, field_list)

    print_list = []
    for print_reo_ix in PRINT_REO_IX_LIST:
        print_list.append (re.sub (A_REO, "", re.sub (BOLD_REO, "",
            xml.sax.saxutils.unescape (field_list[print_reo_ix[0]],
                                       { "&nbsp;" : " "}).strip ())))
    print ("\"" + "\",\"".join (print_list) + "\"")
    return True, removed


def fix_up_url (url):
    """ Prepend http:// or http://www.dice.com as needed; decode ampersand.
    Args: url.
    Returns: possibly modified copy of url.
    """
    # The interior of the if/else is untested, but may occur naturally,
    # which led to writing this code.
    if DICE_REO.search (url) is None:
        if HTTP_REO.search (url) is None:
            url = HTTP_STR + DICE_STR + url
        else:
            sys.stderr.write ("unexpected http:// w/o www.dice.com\n")
            sys.stderr.flush ()
    else:
        if HTTP_REO.search (url) is None:
            url = HTTP_STR + url
    return AMP_REO.sub ("&", url)
        

def read_url (url):
    """ Open and read web page.
    Args: url.
    Returns: bool success flag, web page.
    """
    # The only exception encountered in tests as of 2013 June 22 is HTTPError,
    # file not found.  That is, the code for the other exceptions is untested.
    resp    = ""
    read_ok = False
    try:
        uoob    = urlopen (url)
        resp    = uoob.read ()
        read_ok = True
        uoob.close ()
    except httplib.BadStatusLine as exc:
        sys.stderr.write ('BadStatusLine: ' + str(exc.reason) + "\n"
                          + url + "\n")
        sys.stderr.flush ()
    except httplib.HTTPException as exc:
        sys.stderr.write ('HTTPException: ' + str(exc.reason) + "\n"
                          + url + "\n")
        sys.stderr.flush ()
    except HTTPError as exc:
        sys.stderr.write ("HTTP Error: "    + str (exc.reason) + "\n"
                          + url + "\n")
        sys.stderr.flush ()
    except URLError as exc:
        sys.stderr.write ('URLError: '      + str(exc.reason) + "\n"
                          + url + "\n")
        sys.stderr.flush ()
    return read_ok, resp


def read_url_with_retry (url, nr_tries = 2, delay_sec = 1):
    """ Call read_url up to nr_tries times with delay_sec sleep in between.
    Args: url, nr_tries, delay_sec.
    Returns: bool success flag, web page.
    """
    for try_nr in range (1, nr_tries + 1):
        read_ok, resp = read_url (url)
        if read_ok and resp != "":
            break
        else:
            sleep (delay_sec)
    return read_ok, resp


def process (resp, string_ix, test):
    """ Scrape data for a found after a given offset into a job list page.
    Args: resp job list page, string_ix offset into page.
    Returns: bool has Dice ID, updated string_ix
    """

    # I assume, as has happened in what I've seen, that the job detail link and
    # possibly position, come before the company, which may or may not be there.

    mob = LINK_POSITION_REO.search (resp[string_ix:])
    if mob is None or mob.group ('link') is None:
        sys.stderr.write ("Found no expected link to job detail in job list "
                          "at string_ix " + str (string_ix) + "\n")
        sys.stderr.flush ()
        return False, string_ix

    link = mob.group ('link') if test else fix_up_url (mob.group ('link'))
    position = mob.group ('position')
    if position is None:
        position = ""
        string_ix = min (  len (resp) - 1, string_ix + mob.end ('link')
                         + len ("</a>"))
    else:
        string_ix = min (  len (resp) - 1, string_ix + mob.end ('position')
                         + len ("</a>"))

    # We only want a company that comes before the next job detail link.

    mob = LINK_POSITION_OR_COMPANY_REO.search (resp[string_ix:])
    if mob is None or mob.group ('company') is None:
        company = ""
    else:
        company = mob.group ('company')
        string_ix = min (  len (resp) - 1, string_ix + mob.end ('company')
                         + len ("</a>"))

    read_ok, detail = read_url_with_retry (link)
    if (not read_ok) or detail == "":
        sys.stderr.write ("Detail "
                          + ("not read ok, " if not read_ok else "read ok, ")
                          + ("blank, " if read_ok and detail == "" else "")
                          + link + "\n")
        sys.stderr.flush ()
        return False, string_ix

    dice_idok, removed = process_detail (detail, position, company)
    if not dice_idok:
        sys.stderr.write ("no Dice ID: " + link + (", removed" if removed
                                                   else "") + "\n")
        sys.stderr.flush ()
    return dice_idok, string_ix
                

def get_job_nrs (resp):
    """ Scrape this page start, end, and total job numbers from job list page.
    Args: resp job list page.
    Returns: start, end, total job numbers, bool numbers ok.
    """
    job_nrs_ok = False
    mob = JOB_NRS_REO.search (resp)
    if mob is None:
        start_job_nr = 1 # start > end => read no detail pages; logic in main
                         # line used to use this; superceded by job_nrs_ok now
        end_job_nr   = 0
        nr_jobs      = 0 # end == nr => exit program; superceded by job_nrs_ok
    else:
        start_job_nr = int (mob.group (1))
        end_job_nr   = int (mob.group (2))
        nr_jobs      = int (mob.group (3))
        job_nrs_ok   = True
    return start_job_nr, end_job_nr, nr_jobs, job_nrs_ok


def read_url_job_nrs (url, prev_end_job_nr, nr_tries = 2, delay_sec = 1):
    """ Read job list page continuing a list, with retries.
    Args: job list page url, end job nr to continue after, nr_tries to retry,
          delay_sec sleep between retries.
    Returns: job list page, start, end, total job numbers, bool numbers ok
             (returns 1, 0, 0, False if error).
    """
    read_ok  = False
    resp     = ""
    job_nrs_ok = False
    for try_nr in range (1, nr_tries + 1):
        read_ok, resp = read_url_with_retry (url, nr_tries, delay_sec)
        if read_ok and resp != "":
            start_job_nr, end_job_nr, nr_jobs, job_nrs_ok = get_job_nrs (resp)
            if job_nrs_ok:
                return resp, start_job_nr, end_job_nr, nr_jobs, job_nrs_ok
            else:
                sleep (delay_sec)
        else:
            sleep (delay_sec)

    # At this point job_nrs_ok is False; relied upon in else and return.

    if (not read_ok) or resp == "":
        sys.stderr.write ("Error reading page that should follow job number "
                          + str (prev_end_job_nr) + "\n")
        sys.stderr.flush ()
    else:
        sys.stderr.write ("Error processing page that should follow job number "
                          + str (prev_end_job_nr) + "; obtained:\n")
        sys.stderr.write ("*************************\n")
        sys.stderr.write (resp) # verbose but could be informative
        sys.stderr.write ("*************************\n")
        sys.stderr.write ("Can't process page that should have list of jobs\n")
        sys.stderr.flush ()
    return resp, 1, 0, 0, False


def main_func (args):
    """ Scrape jobs; called by main.
    Args: args, set to sys.argv by main or set directly for testing.
    Returns: nothing
    """

    url_base = "http://www.dice.com/job/results?"
    nr_args  = len (args)

    if (   nr_args == 1
        or (    nr_args == 3
            and args[2] != "title"
            and args[2] != "test")
        or nr_args > 3):
        print ("""Usage:  python dice_scrape.py "search term"
or      python dice_scrape.py "search term" title
        to require that the search term be found in the title
or      python dice_scrape.py "test_url" test
        for test with e.g. what's in the pages subdirectory: test_http_server,
        test_url=http://localhost:8000/test.html or testnojobnrs, and any pages
        they link to, such as job*.html.""")
        return 1

    search_str = args[1]
    param_map  = { "caller" : "basic", "o" : "0", "q" : search_str,
                   "src" : "19", "x" : "all", "p" : "" }
    test       = False
    if nr_args == 3:
        if args[2] == "title":
            param_map["j"] = "true"
        elif args[2] == "test":
            test = True
            test_url = args[1]

    # I don't use a for loop b/c the number of jobs might change during
    # execution.  I hope that not too much changes during execution; it
    # would be nice if newly posted jobs came at the end, but I suspect,
    # because they're not displayed in order of date posted, they may
    # come anywhere.  So additions might result in duplicate jobs, but
    # hopefully at least not lost ones.

    end_job_nr   = 0
    nr_dice_id   = 0
    nr_no_dice_id = 0

    while True:
        param_map["o"] = str (end_job_nr)
        if test:
            next_url = test_url
        else:
            next_url = url_base + urlencode (param_map)
        sys.stderr.write (next_url + "\n")
        sys.stderr.flush ()
        resp, start_job_nr, end_job_nr, nr_jobs, job_nrs_ok = (
            read_url_job_nrs (next_url, end_job_nr, 3, 2))  # more than defaults
        if not job_nrs_ok:
            break

        sys.stderr.write ("processing job_nrs " + str (start_job_nr)
                          + " through " + str (end_job_nr) + "\n")
        sys.stderr.flush ()
        string_ix = 0
        for job_nr in range (start_job_nr, end_job_nr + 1):
            dice_idok, string_ix = process (resp, string_ix, test)
            if dice_idok:
                if test:
                    sys.stderr.write ("dice id ok\n")
                    sys.stderr.flush ()
                nr_dice_id   = nr_dice_id   + 1
            else:
                sys.stderr.write ("dice id not ok\n")
                sys.stderr.flush ()
                nr_no_dice_id = nr_no_dice_id + 1
        if end_job_nr == nr_jobs:
            break
    
    sys.stderr.write ("nr with Dice ID " + str (nr_dice_id)
                      + ", nr without " + str (nr_no_dice_id) + "\n")
    sys.stderr.flush ()
    return 0

def main ():
    """ dice_scrape main to scrape jobs; simply calls main_func.
    Args: none
    Returns: exit code
    """
    return main_func (sys.argv)

if __name__ == "__main__":
    main ()
