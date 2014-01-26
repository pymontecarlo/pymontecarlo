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
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.program.penepma.converter import Converter
from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import PencilBeam
from pymontecarlo.options.detector import TimeDetector
from pymontecarlo.options.limit import TimeLimit

# Globals and constants variables.
warnings.simplefilter("always")

class TestPenelopeConverter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.converter = Converter((0.1, 0.2), 51.2, 53.4)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testconvert_pencilbeam(self):
        # Base options
        ops = Options(name="Test")
        ops.beam = PencilBeam(1234)
        ops.detectors['det1'] = TimeDetector()
        ops.limits.add(TimeLimit(100))

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            opss = self.converter.convert(ops)

        # 7 warning:
        # PencilBeam -> GaussianBeam
        # Set default models (6)
        self.assertEqual(1, len(opss))
        self.assertEqual(7, len(ws))

        # Test
        self.assertAlmostEqual(1234, opss[0].beam.energy_eV, 4)
        self.assertAlmostEqual(0.0, opss[0].beam.diameter_m, 4)

        self.assertEqual(6, len(opss[0].models))

    def testconvert_nolimit(self):
        # Base options
        ops = Options(name="Test")

        # Convert
        opss = self.converter.convert(ops)

        # Test
        self.assertEqual(0, len(opss))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
