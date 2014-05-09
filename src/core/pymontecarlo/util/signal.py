#!/usr/bin/env python
"""
================================================================================
:mod:`signal` -- Signal pattern
================================================================================

.. module:: signal
   :synopsis: signal pattern

.. inheritance-diagram:: pyhmsa.util.signal

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

class Signal(object):

    def __init__(self):
        self._handlers = set()

    def __call__(self, *args):
        self.fire(*args)

    def connect(self, handler):
        self._handlers.add(handler)

    def fire(self, *args):
        for handler in self._handlers:
            handler(*args)
