#!/usr/bin/env python
"""
================================================================================
:mod:`queue` -- Queue for runner and creator
================================================================================

.. module:: queue
   :synopsis: Queue for runner and creator

.. inheritance-diagram:: pymontecarlo.runner.base.queue

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from Queue import Queue

# Third party modules.

# Local modules.

# Globals and constants variables.

class OptionsQueue(Queue):
    def __init__(self, maxsize=0):
        Queue.__init__(self, maxsize)

        self._exc = None

    def are_all_tasks_done(self):
        if self._exc is not None:
            raise self._exc
        return self.unfinished_tasks == 0 and self.empty()

    def raise_exc(self, exc):
        self._exc = exc

