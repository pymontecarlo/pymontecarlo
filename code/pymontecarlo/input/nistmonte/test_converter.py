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
from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.detector import PhotonSpectrumDetector
from pymontecarlo.input.base.limit import ShowersLimit
from pymontecarlo.input.nistmonte.converter import Converter, ConversionException

# Globals and constants variables.
warnings.simplefilter("always")

class TestConverter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.converter = Converter()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testconvert1(self):
        # Base options
        ops = Options("Test")
        ops.limits.add(ShowersLimit(1234))

        det = PhotonSpectrumDetector((radians(35), radians(45)),
                                     (0, radians(360.0)),
                                     (0.0, 1234), 100)
        ops.detectors['det1'] = det

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            self.converter.convert(ops)

        self.assertEqual(5, len(ws))

        self.assertEqual(1, len(ops.detectors))

        self.assertEqual(1, len(ops.limits))
        limit = ops.limits.find(ShowersLimit)
        self.assertEqual(1234, limit.showers)

        self.assertEqual(5, len(ops.models))

    def testconvert2(self):
        # Base options
        ops = Options("Test")

        # No showers limit
        self.assertRaises(ConversionException, self.converter.convert, ops)

    def testconvert3(self):
        # Base options
        ops = Options("Test")
        ops.limits.add(ShowersLimit(1234))

        det = PhotonSpectrumDetector((radians(35), radians(45)),
                                     (0, radians(360.0)),
                                     (0.0, 1234), 100)
        ops.detectors['det1'] = det

        det = PhotonSpectrumDetector((radians(30), radians(50)),
                                     (0, radians(360.0)),
                                     (0.0, 1234), 100)
        ops.detectors['det2'] = det

        # Two detectors should have the same elevation
        self.assertRaises(ConversionException, self.converter.convert, ops)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
