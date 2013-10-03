""" Contains configuration variables that can be set before import dice_scrape.
dice_scrape_cfg.py v2 rev 2013 June 23 by Stuart Ambler.
Copyright (c) 2013 Stuart Ambler.
Distributed under the Boost License in the accompanying file LICENSE.
Example:  dice_scrape_cfg.ALL_FIELDS = True
          import dice_scrape
Only the read and write bool variables in FIELD_LIST elements should be changed,
and if write is True, read must also be True.  They govern whether an attempt is
made to read (scrape) the field, and whether it's output by the scraper.
Special indicates something other than the usual <dt>, <dd>, <td> schemes as in
the regular expressions in dice_scrape.py.  Company is read even if not written,
to avoid special cases in logic.  order is for output.
"""
ALL_FIELDS = False
FIELD_LIST = [ #label,      name,              read,  write, special, order
(r'Area Code\s*:?',         "area_code",       True,  True,  False,   5),
(r'Company\s*:?',           "company",         True,  False, False,   7),
(r'Date Posted\s*:?',       "date_posted",     False, False, False,   8),
(r'Dice ID\s*:?',           "dice_id",         True,  True,  False,   1),
(r'(?:Job )?Length\s*:?',   "length",          True,  True,  False,   4),
(r'(?:Job )?Location\s*:?', "location",        False, False, False,   9),
(r'(?:Pay Rate|Base Pay)'
 r'\s*:?',                  "pay_rate",        False, False, False,  10),
(r'(?:Position ID|Job Number|Job Ref. Code|Reference Code)\s*:?',
                            "position_id",     True,  True,  False,   0),
(r'Skills\s*:?',            "skills",          False, False, False,  11),
(r'(?:(?:Employee|Employ.) Type|Tax Term|Job Status(?:\s*/\s*Type)?'
 r'|Status)\s*:?',          "tax_term",        True,  True,  False,   3),
(r'Telecommute\s*:?',       "telecommute",     False, False, False,  12),
(r'Travel Required\s*:?',   "travel_required", False, False, False,  13),
(r'(?P<data>.)',            "position",        True,  True,  True,    2),
(r'(?P<data>T)his job has been removed from our site',
                            "removed",         True,  True,  True,    6)]
