#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.util.cbook import normalize_angle

# Globals and constants variables.

class TestCbookModule(TestCase):

    def testnormalize_angle(self):
        self.assertAlmostEqual(math.radians(40), normalize_angle(math.radians(40)), 4)
        self.assertAlmostEqual(math.radians(320), normalize_angle(math.radians(-40)), 4)
        self.assertAlmostEqual(math.radians(320), normalize_angle(math.radians(-400)), 4)
        self.assertAlmostEqual(math.radians(40), normalize_angle(math.radians(400)), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
