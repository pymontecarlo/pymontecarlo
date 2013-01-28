#!/usr/bin/env python
"""
================================================================================
:mod:`config_setup` -- NISTMonte Monte Carlo setup configuration
================================================================================

.. module:: config_setup
   :synopsis: NISTMonte Monte Carlo setup configuration

.. inheritance-diagram:: pymontecarlo.program.nistmonte.config_setup

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

class _NISTMonteSetup(Setup):

    def __init__(self):
        packages = \
            ['pymontecarlo.program.nistmonte',
             'pymontecarlo.program.nistmonte.input',
             'pymontecarlo.program.nistmonte.runner']

        Setup.__init__(self, packages)

setup = _NISTMonteSetup()
