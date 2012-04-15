#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- Base configuration interface of all Monte Carlo programs
================================================================================

.. module:: config
   :synopsis: Base configuration interface of all Monte Carlo programs

.. inheritance-diagram:: pymontecarlo.program.config

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

class ProgramConfiguration(object):

    def _get_name(self):
        raise NotImplementedError

    name = property(_get_name, doc="Full program name")

    def _get_alias(self):
        raise NotImplementedError

    alias = property(_get_alias, doc="Short program name")

    def is_valid(self):
        return False

    def _get_converter(self):
        raise NotImplementedError

    converter = property(_get_converter, doc="Converter class of program")

    def _get_exporter(self):
        raise NotImplementedError

    exporter = property(_get_exporter, doc="Exporter class of program")

    def _get_importer(self):
        raise NotImplementedError

    importer = property(_get_importer, doc="Importer class of program")

    def _get_worker(self):
        raise NotImplementedError

    worker = property(_get_worker, doc="Worker class of program")
