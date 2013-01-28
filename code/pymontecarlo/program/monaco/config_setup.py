#!/usr/bin/env python
"""
================================================================================
:mod:`config_setup` -- Monaco Monte Carlo setup configuration
================================================================================

.. module:: config_setup
   :synopsis: Monaco Monte Carlo setup configuration

.. inheritance-diagram:: pymontecarlo.program.monaco.config_setup

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
from pymontecarlo.program.config_setup import Setup

# Globals and constants variables.

class _MonacoSetup(Setup):

    def __init__(self):
        packages = \
            ['pymontecarlo.program.monaco',
             'pymontecarlo.program.monaco.input',
             'pymontecarlo.program.monaco.io',
             'pymontecarlo.program.monaco.runner']

        Setup.__init__(self, packages)

setup = _MonacoSetup()
