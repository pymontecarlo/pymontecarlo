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

from pymontecarlo.program.monaco.converter import Converter

from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import PencilBeam
from pymontecarlo.options.detector import PhotonIntensityDetector
from pymontecarlo.options.limit import ShowersLimit

# Globals and constants variables.

class TestConverter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.converter = Converter()

    def tearDown(self):
        TestCase.tearDown(self)

    def testconvert1(self):
        # Base options
        ops = Options(name="Test")
        ops.beam = PencilBeam(1234)
        ops.detectors['xrays'] = PhotonIntensityDetector((0.1, 0.2), (0.3, 0.4))
        ops.limits.add(ShowersLimit(5678))

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            opss = self.converter.convert(ops)

        # 6 warnings for the default models
        self.assertEqual(6, len(ws))
        self.assertEqual(1, len(opss))

        # Test
        self.assertAlmostEqual(1234, opss[0].beam.energy_eV, 4)

        self.assertEqual(1, len(opss[0].detectors))

        self.assertEqual(1, len(opss[0].limits))
        limit = list(ops.limits.iterclass(ShowersLimit))[0]
        self.assertEqual(5678, limit.showers)

        self.assertEqual(5, len(opss[0].models))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
