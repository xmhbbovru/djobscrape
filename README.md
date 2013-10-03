README.md rev. 02 October 2013 by Stuart Ambler.
Copyright (c) 2013 Stuart Ambler.
Distributed under the Boost License in the accompanying file LICENSE.

Dice Jobs Scraper in Python
========
- Scraper of jobs from www.dice.com, emulating what the user could do.

- Usage: python dice\_scrape.py "search term"

- or     python dice\_scrape.py "search term" title
to require that the search term be found in the title, for Dice's option to
search title only,

- or     python dice\_scrape.py "test\_url" test
for test with e.g. what's in the pages subdirectory: test\_http\_server,
test\_url=http://localhost:8000/test.html or testnojobnrs.html, and any pages
 they link to, such as job*.html.

- stdout: comma separated quoted string values, one line per job:
position\_id, dice\_id, position, taxterm, length, areacode, removed; or more
fields if global variable ALL\_FIELDS at the top of dice\_scrape\_cfg.py is True.

- stderr: is used for informational as well as error messages.

- Tested with Python 2.7.3.  For Python 3, issues e.g. of byte vs. string
patterns for re need to be resolved.

What the files are for
======================
- needed for use w/o testing or changes:
  * dice\_scrape\_cfg.py sets global variable config info for dice\_scrape.py
  * dice\_scrape.py is the scraper

- androidtitle out,err (not on GitHub here as they contain Dice data) are output from Android title test as in tardicescrape; a human needs to look at them

- makecompareall.py makes the correct out,err files for ALL\_FIELDS

- makecomparenojobnrs.py makes the correct out,err files, no jobnrs, not ALL

- makecomparenonexistent.py makes the correct out,err files, nonexistent, not ALL

- makecompare.py makes the correct out,err files; normal, not ALL\_FIELDS

- testout,err* are the "correct" output from various tests

- testpytest.py is the main test module, testing "ALL\_FIELDS"; run with python - m pytest testpytest.py; after a half minute or minute it should say 3 passed

- testpytestnotall.py is the same but not testing "ALL\_FIELDS"; run with python - m pytest testpytestnotall.py; after a half minute or minute it should say 3 passed

- pages/cgi-bin/test\_cgi.py tests the simple http server directly

- pages/job*.html are test data

- pages/test\_http\_server.py is a simple http server to use for testing


Notes
======================
- Tested on an IBM Thinkpad SL510, 8 GB RAM, 64 bit Lubuntu 12.10.

- Thanks to the Economic Policy Institute for their support of this project.

- I'd be happy to hear from you.  My [website](http://www.zulazon.com) has a
contact form.
