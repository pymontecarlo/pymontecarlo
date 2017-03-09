#!/usr/bin/env python
""" """

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
        super().setUp()

        self.comp1 = {29: 1.0}
        self.comp2 = {29: 0.5, 30: 0.5}

    def testkanaya_okayama(self):
        self.assertAlmostEqual(1.45504, kanaya_okayama(self.comp1, 20e3) * 1e6, 4)
        self.assertAlmostEqual(1.61829, kanaya_okayama(self.comp2, 20e3) * 1e6, 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
