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
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.program.monaco.input.converter import Converter

from pymontecarlo.input.options import Options
from pymontecarlo.input.beam import PencilBeam
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.input.limit import ShowersLimit

# Globals and constants variables.

class TestConverter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.converter = Converter()

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testconvert1(self):
        # Base options
        ops = Options(name="Test")
        ops.beam = PencilBeam(1234)
        ops.detectors['xrays'] = PhotonIntensityDetector((0.1, 0.2), (0.3, 0.4))
        ops.limits.add(ShowersLimit(5678))

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            self.converter.convert(ops)

        # 6 warnings for the default models
        self.assertEqual(6, len(ws))

        # Test
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)

        self.assertEqual(1, len(ops.detectors))

        self.assertEqual(1, len(ops.limits))
        limit = ops.limits.find(ShowersLimit)
        self.assertEqual(5678, limit.showers)

        self.assertEqual(5, len(ops.models))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
