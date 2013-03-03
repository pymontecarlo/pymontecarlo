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

from pymontecarlo.util.sort import topological_sort

# Globals and constants variables.

class TestModule(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testtopological_sort(self):
        d = { 'a' : dict(b=1, c=1), 'c' : dict(d=1), 'd' : dict(e=1, f=1, g=1), 'h' : dict(j=1)}

        actuals = list(topological_sort(d, 'a'))
        expecteds = ['e', 'g', 'f', 'd', 'c', 'b', 'a']
        self.assertEqual(expecteds, actuals)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
