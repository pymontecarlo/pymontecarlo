#!/usr/bin/env python
"""
================================================================================
:mod:`config_cli` -- Base configuration of the command line interface
================================================================================

.. module:: config_cli
   :synopsis: Base configuration of the command line interface

.. inheritance-diagram:: pymontecarlo.program.config_cli

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

class CLI(object):

    def configure(self, console, settings):
        """
        Configures the settings of this program.
        The method should only exit if the settings of this program are valid.
        """
        pass
