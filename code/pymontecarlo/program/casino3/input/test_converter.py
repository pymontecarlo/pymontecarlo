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

from pymontecarlo.program.casino3.input.converter import Converter, ConversionException
from pymontecarlo.input.options import Options
from pymontecarlo.input.beam import PencilBeam
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.detector import TrajectoryDetector

# Globals and constants variables.
warnings.simplefilter("always")

class TestPenelopeConverter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.converter = Converter()

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testconvert_pencilbeam(self):
        # Base options
        ops = Options(name="Test")
        ops.beam = PencilBeam(1234)
        ops.limits.add(ShowersLimit(100))
        ops.detectors['trajectories'] = TrajectoryDetector(100)

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            self.converter.convert(ops)

        # 7 warning:
        # PencilBeam -> GaussianBeam
        # Set default models (5)
        self.assertEqual(6, len(ws))

        # Test
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)
        self.assertAlmostEqual(0.0, ops.beam.diameter_m, 4)

        self.assertEqual(5, len(ops.models))

    def testconvert_nodetector(self):
        # Base options
        ops = Options(name="Test")
        ops.limits.add(ShowersLimit(100))

        # Convert
        self.assertRaises(ConversionException, self.converter.convert , ops)

    def testconvert_nolimit(self):
        # Base options
        ops = Options(name="Test")
        ops.detectors['trajectories'] = TrajectoryDetector(100)

        # Convert
        self.assertRaises(ConversionException, self.converter.convert , ops)

    def testconvert_showers_not_equal(self):
        # Base options
        ops = Options(name="Test")
        ops.limits.add(ShowersLimit(200))
        ops.detectors['trajectories'] = TrajectoryDetector(100)

        # Convert
        self.assertRaises(ConversionException, self.converter.convert , ops)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
