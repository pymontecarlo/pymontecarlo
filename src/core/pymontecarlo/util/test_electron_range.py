#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.util.electron_range import kanaya_okayama

# Globals and constants variables.

class TestModule(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.comp1 = {29: 1.0}
        self.comp2 = {29: 0.5, 30: 0.5}

    def tearDown(self):
        TestCase.tearDown(self)

    def testkanaya_okayama(self):
        self.assertAlmostEqual(1.45504, kanaya_okayama(self.comp1, 20e3) * 1e6, 4)
        self.assertAlmostEqual(1.61829, kanaya_okayama(self.comp2, 20e3) * 1e6, 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
