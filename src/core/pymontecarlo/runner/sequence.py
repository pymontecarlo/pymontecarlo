#!/usr/bin/env python
"""
================================================================================
:mod:`sequence` -- Adaptor to run sequences.
================================================================================

.. module:: sequence
   :synopsis: Runner to run sequences.

.. inheritance-diagram:: pymontecarlo.runner.sequence

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.runner.base import _Runner

# Globals and constants variables.

class SequenceRunner(_Runner):

    def __init__(self, runner):
        _Runner.__init__(self, runner.program)
        self._runner = runner

    def put(self, options_seq):
        pass

    def start(self):
        self._runner.start()

    def stop(self):
        self._runner.stop()

    def close(self):
        self._runner.close()

    def is_alive(self):
        return self._runner.is_alive()

    def join(self):
        self._runner.join()

    def get_results(self):
        pass

    def report(self):
        return self._runner.report()

