#!/usr/bin/env python
"""
================================================================================
:mod:`sort` -- Sort utilities
================================================================================

.. module:: sort
   :synopsis: Sort utilities

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

def topological_sort(d, k):
    """
    Togological sort.
    http://stackoverflow.com/questions/108586/topological-sort-recursive-using-generators
    """
    for ii in d.get(k, []):
        for jj in topological_sort(d, ii):
            yield jj
    yield k
