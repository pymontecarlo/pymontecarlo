#!/usr/bin/env python
"""
================================================================================
:mod:`config_setup` -- WinXRay Monte Carlo setup configuration
================================================================================

.. module:: config_setup
   :synopsis: WinXRay Monte Carlo setup configuration

.. inheritance-diagram:: pymontecarlo.program.winxray.config_setup

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

import winxrayTools
import DatabasesTools

# Globals and constants variables.

class _WinXRaySetup(Setup):

    def __init__(self):
        packages = ['pymontecarlo.program.winxray',
                    'pymontecarlo.program.winxray.input',
                    'pymontecarlo.program.winxray.output',
                    'pymontecarlo.program.winxray.runner',
                    'winxrayTools.Configuration',
                    'winxrayTools.ResultsFile']
        py_modules = \
            ['winxrayTools.__init__', 'DatabasesTools.ElementProperties']
        package_dir = \
            {'winxrayTools': os.path.dirname(winxrayTools.__file__),
             'DatabasesTools': os.path.dirname(DatabasesTools.__file__)}
        package_data = {'winxrayTools.Configuration': ['default.wxc']}

        Setup.__init__(self, packages, py_modules, package_dir, package_data)

setup = _WinXRaySetup()
