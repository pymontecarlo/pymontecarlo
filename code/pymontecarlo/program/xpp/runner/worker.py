#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- XPP worker
================================================================================

.. module:: worker
   :synopsis: XPP worker

.. inheritance-diagram:: pymontecarlo.program.xpp.runner.worker

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
from pymontecarlo.program.pouchou.runner.worker import _PouchouWorker
from PouchouPichoirModels.models.XPP import XPP

# Globals and constants variables.

class Worker(_PouchouWorker):
    _MODEL_CLASS = XPP
