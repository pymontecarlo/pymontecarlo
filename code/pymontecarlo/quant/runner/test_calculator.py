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

# Third party modules.

# Local modules.
from pymontecarlo.quant.runner.calculator import SimpleCalculator

# Globals and constants variables.

class TestSimpleCalculator(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        
        stdintensities = {29: (2.0, 0.2), 79: (4.0, 0.4)}
        
        self.calc = SimpleCalculator(None, stdintensities)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcalculate(self):
        unkintensities = {29: (1.0, 0.1), 79: (2.0, 0.2)}
        kratio = self.calc.calculate(unkintensities)

        self.assertAlmostEqual(0.5, kratio[29][0], 4)
        self.assertAlmostEqual(0.07071, kratio[29][1], 4)

        self.assertAlmostEqual(0.5, kratio[79][0], 4)
        self.assertAlmostEqual(0.07071, kratio[79][1], 4)
        
if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
