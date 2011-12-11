#!/usr/bin/env python
"""
================================================================================
:mod:`results` -- Main container of all results
================================================================================

.. module:: results
   :synopsis: Main container of all results

.. inheritance-diagram:: results

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from collections import Mapping

# Third party modules.

# Local modules.

# Globals and constants variables.

class Results(Mapping):

    def __init__(self, options, results={}):
        self._options = options
        self._results = dict(results) # copy

    @property
    def options(self):
        return self._options

    def __len__(self):
        return len(self._results)

    def __getitem__(self, key):
        return self._results[key]

    def __iter__(self):
        return iter(self._results)


