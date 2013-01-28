#!/usr/bin/env python
"""
================================================================================
:mod:`config_setup` -- Pouchou PAP setup configuration
================================================================================

.. module:: config_setup
   :synopsis: Pouchou PAP setup configuration

.. inheritance-diagram:: pymontecarlo.program.pap.config_setup

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
from pymontecarlo.program._pouchou.config_setup import _PouchouSetup

# Globals and constants variables.

class _XPPSetup(_PouchouSetup):

    def __init__(self):
        packages = \
            ['pymontecarlo.program.xpp',
             'pymontecarlo.program.xpp.runner']
        _PouchouSetup.__init__(self, packages)

setup = _XPPSetup()
