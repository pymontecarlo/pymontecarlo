#!/usr/bin/env python
"""
================================================================================
:mod:`exporter` -- Base class for exporters
================================================================================

.. module:: exporter
   :synopsis: Base class for exporters

.. inheritance-diagram:: pymontecarlo.input.base.exporter

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

class Exporter(object):
    def export(self, options):
        raise NotImplementedError
