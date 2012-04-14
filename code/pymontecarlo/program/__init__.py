#!/usr/bin/env python
"""
================================================================================
:mod:`program` -- Base interface of all Monte Carlo programs
================================================================================

.. module:: program
   :synopsis: Base interface of all Monte Carlo programs

.. inheritance-diagram:: pymontecarlo.program

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

# Globals and constants variables.

class Program(object):

    def get_name(self):
        raise NotImplementedError

    def get_alias(self):
        raise NotImplementedError

    def is_valid(self):
        return False

    def get_converter(self):
        raise NotImplementedError

    def get_exporter(self):
        raise NotImplementedError

    def get_importer(self):
        raise NotImplementedError

    def get_worker(self):
        raise NotImplementedError
