#!/usr/bin/env python
"""
================================================================================
:mod:`testcase` -- Common test case for all unit tests
================================================================================

.. module:: testcase
   :synopsis: Common test case for all unit tests

.. inheritance-diagram:: pymontecarlo.testcsse

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import unittest

# Third party modules.

# Local modules.
from pymontecarlo import load_settings, _set_settings

# Globals and constants variables.

basepath = os.path.dirname(__file__)
filepath = os.path.join(basepath, 'testdata', 'settings.cfg')
settings = load_settings([filepath])

class TestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        _set_settings(settings)

