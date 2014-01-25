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
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import PhotonIntensityDetector
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.program.nistmonte.converter import Converter

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
        ops = Options("Test")
        ops.beam.origin_m = (0.0, 0.0, 0.09)
        ops.limits.add(ShowersLimit(1234))

        det = PhotonIntensityDetector((radians(35), radians(45)),
                                      (0, radians(360.0)))
        ops.detectors['det1'] = det

        # Convert
        opss = self.converter.convert(ops)

        self.assertEqual(1, len(opss))

        self.assertEqual(1, len(opss[0].detectors))

        self.assertEqual(1, len(opss[0].limits))
        limit = list(ops.limits.iterclass(ShowersLimit))[0]
        self.assertEqual(1234, limit.showers)

        self.assertEqual(6, len(opss[0].models))

    def testconvert2(self):
        # Base options
        ops = Options("Test")
        ops.beam.origin_m = (0.0, 0.0, 0.09)

        det = PhotonIntensityDetector((radians(35), radians(45)),
                                      (0, radians(360.0)))
        ops.detectors['det1'] = det

        # Convert
        opss = self.converter.convert(ops)

        self.assertEqual(0, len(opss)) # No showers limit

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
