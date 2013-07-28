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
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.program._pouchou.input.converter import Converter

# Globals and constants variables.
warnings.simplefilter("always")

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

        det = PhotonIntensityDetector((radians(35), radians(45)),
                                      (0, radians(360.0)))
        ops.detectors['det1'] = det

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            opss = self.converter.convert(ops)

        self.assertEqual(2, len(ws)) # GaussianBeam, model for MAC
        self.assertEqual(1, len(opss))

        self.assertEqual(1, len(opss[0].detectors))
        self.assertEqual(1, len(opss[0].models))

    def testconvert2(self):
        # Base options
        ops = Options("Test")

        det = PhotonIntensityDetector((radians(35), radians(45)),
                                      (0, radians(360.0)))
        ops.detectors['det1'] = det

        det = PhotonIntensityDetector((radians(35), radians(45)),
                                      (0, radians(360.0)))
        ops.detectors['det2'] = det

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            opss = self.converter.convert(ops)

        self.assertEqual(4, len(ws)) # GaussianBeam, model for MAC
        self.assertEqual(2, len(opss))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
