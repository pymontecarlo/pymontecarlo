#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Casino 2 worker
================================================================================

.. module:: worker
   :synopsis: Casino 2 worker

.. inheritance-diagram:: pymontecarlo.program.casino2.runner.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.runner.worker import Worker as _Worker

# Globals and constants variables.

class Worker(_Worker):
    def __init__(self, queue_options, outputdir, workdir=None, overwrite=True):
        """
        Runner to run Monaco simulation(s).
        """
        _Worker.__init__(self, queue_options, outputdir, workdir, overwrite)
