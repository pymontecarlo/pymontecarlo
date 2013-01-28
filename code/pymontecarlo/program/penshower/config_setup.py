#!/usr/bin/env python
"""
================================================================================
:mod:`config_setup` -- PENSHOWER Monte Carlo setup configuration
================================================================================

.. module:: config_setup
   :synopsis: PENSHOWER Monte Carlo setup configuration

.. inheritance-diagram:: pymontecarlo.program.penshower.config_setup

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
from pymontecarlo.program._penelope.config_setup import _PenelopeSetup

# Globals and constants variables.

class _PenshowerSetup(_PenelopeSetup):

    def __init__(self):
        packages = \
            ['pymontecarlo.program.penshower',
             'pymontecarlo.program.penshower.input',
             'pymontecarlo.program.penshower.io',
             'pymontecarlo.program.penshower.runner']

        _PenelopeSetup.__init__(self, packages)

setup = _PenshowerSetup()
