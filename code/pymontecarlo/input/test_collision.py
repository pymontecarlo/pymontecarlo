#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import copy

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.input.collision import DELTA

# Globals and constants variables.

class TestCollision(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test__str__(self):
        self.assertEqual('delta', str(DELTA))
        self.assertEqual(1, int(DELTA))

    def test__repr__(self):
        self.assertEqual('<Delta>', repr(DELTA))

    def test__copy__(self):
        self.assertIs(DELTA, copy.copy(DELTA))
        self.assertIs(DELTA, copy.deepcopy(DELTA))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
