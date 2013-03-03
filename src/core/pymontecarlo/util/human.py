#!/usr/bin/env python
"""
================================================================================
:mod:`human` -- Utility functions to represent values in a more human format
================================================================================

.. module:: human
   :synopsis: Utility functions to represent values in a more human format

.. inheritance-diagram:: human

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import re

# Third party modules.

# Local modules.

# Globals and constants variables.
_REGEX_CAMEL_CASE = re.compile('([a-z0-9])([A-Z])')

def human_time(time_s):
    """
    Converts a time in seconds to a string using days, hours, minutes and seconds.
    """
    time_s = int(time_s) # Ensure int

    out = []

    days = time_s / 86400
    if days == 1:
        out.append('%i day' % days)
        time_s -= days * 86400
    elif days >= 1:
        out.append('%i days' % days)
        time_s -= days * 86400

    hours = time_s / 3600
    if hours >= 1:
        out.append('%i hr' % hours)
        time_s -= hours * 3600

    minutes = time_s / 60
    if minutes >= 1:
        out.append('%i min' % minutes)
        time_s -= minutes * 60

    if time_s >= 1:
        out.append('%i sec' % time_s)

    return ' '.join(out)

def camelcase_to_words(text):
    return _REGEX_CAMEL_CASE.sub(r'\1 \2', text)
