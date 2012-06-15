#!/usr/bin/env python
"""
================================================================================
:mod:`queue` -- Queue for runner and creator
================================================================================

.. module:: queue
   :synopsis: Queue for runner and creator

.. inheritance-diagram:: pymontecarlo.runner.queue

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import sys
import traceback
from Queue import Queue as _Queue

# Third party modules.

# Local modules.

# Globals and constants variables.

class Queue(_Queue):
    def __init__(self, maxsize=0):
        _Queue.__init__(self, maxsize)

        self._exc_info = None

    def are_all_tasks_done(self):
        if self._exc_info is not None:
            traceback.print_exception(*self._exc_info)
            raise self._exc_info[1]

        return self.unfinished_tasks == 0 and self.empty()

    def raise_exception(self):
        self._exc_info = sys.exc_info()

    def join(self):
        self.all_tasks_done.acquire()
        try:
            while self.unfinished_tasks:
                self.all_tasks_done.wait(1)

                if self._exc_info is not None:
                    traceback.print_exception(*self._exc_info)
                    raise self._exc_info[1]
        finally:
            self.all_tasks_done.release()


