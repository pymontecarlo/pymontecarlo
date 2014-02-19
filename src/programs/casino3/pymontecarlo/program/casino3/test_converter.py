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

from pymontecarlo.program.casino3.converter import Converter
from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import PencilBeam
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.detector import TrajectoryDetector

# Globals and constants variables.

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
        ops.detectors['trajectories'] = TrajectoryDetector(False)

        # Convert
        opss = self.converter.convert(ops)

        # Test
        self.assertEqual(1, len(opss))

        self.assertAlmostEqual(1234, opss[0].beam.energy_eV, 4)
        self.assertAlmostEqual(0.0, opss[0].beam.diameter_m, 4)

        self.assertEqual(5, len(opss[0].models))

    def testconvert_nolimit(self):
        # Base options
        ops = Options(name="Test")
        ops.detectors['trajectories'] = TrajectoryDetector(False)

        # Convert
        opss = self.converter.convert(ops)

        # Test
        self.assertEqual(0, len(opss))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
