#!/usr/bin/env python
"""
================================================================================
:mod:`config_setup` -- Casino 2 Monte Carlo setup configuration
================================================================================

.. module:: config_setup
   :synopsis: Casino 2 Monte Carlo setup configuration

.. inheritance-diagram:: pymontecarlo.program.casino2.config_setup

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os

# Third party modules.

# Local modules.
from pymontecarlo.program.config_setup import Setup

import casinoTools

# Globals and constants variables.

class _Casino2Setup(Setup):

    def __init__(self):
        packages = \
            ['pymontecarlo.program.casino2',
             'pymontecarlo.program.casino2.input',
             'pymontecarlo.program.casino2.io',
             'pymontecarlo.program.casino2.runner',
             'casinoTools.FileFormat.casino2']
        py_modules = \
            ['casinoTools.__init__',
             'casinoTools.FileFormat.__init__',
             'casinoTools.FileFormat.XrayRadial',
             'casinoTools.FileFormat.casino3.FileReaderWriterTools']
        package_dir = \
            {'casinoTools': os.path.dirname(casinoTools.__file__)}
        package_data = \
            {'pymontecarlo.program.casino2.io': ['templates/*.sim']}

        Setup.__init__(self, packages, py_modules, package_dir, package_data)

setup = _Casino2Setup()
