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

from pymontecarlo.program.penepma.input.converter import Converter, ConversionException
from pymontecarlo.input.options import Options
from pymontecarlo.input.beam import PencilBeam
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.input.limit import TimeLimit

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
        ops.limits.add(TimeLimit(100))

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            self.converter.convert(ops)

        # 7 warning:
        # PencilBeam -> GaussianBeam
        # Set default models (6)
        self.assertEqual(7, len(ws))

        # Test
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)
        self.assertAlmostEqual(0.0, ops.beam.diameter_m, 4)

        self.assertEqual(6, len(ops.models))

    def testconvert_nolimit(self):
        # Base options
        ops = Options(name="Test")

        # Convert
        self.assertRaises(ConversionException, self.converter.convert , ops)

    def testconvert_photondetector(self):
        # Base options
        ops = Options(name="Test")
        ops.detectors['xray1'] = \
            PhotonIntensityDetector((radians(35), radians(45)), (0, radians(360.0)))
        ops.limits.add(TimeLimit(100))

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            self.converter.convert(ops)

        # 7 warning:
        # Set default models (6)
        # 1 for PhotonIntensityDetector to PhotonSpectrumDetector 
        self.assertEqual(7, len(ws))

        self.assertEqual(1, len(ops.detectors))

        det = ops.detectors['xray1']
        self.assertAlmostEqual(det.elevation_rad[0], radians(35), 4)
        self.assertAlmostEqual(det.elevation_rad[1], radians(45), 4)
        self.assertAlmostEqual(det.azimuth_rad[0], radians(0), 4)
        self.assertAlmostEqual(det.azimuth_rad[1], radians(360), 4)
        self.assertAlmostEqual(det.limits_eV[0], 0.0, 4)
        self.assertAlmostEqual(det.limits_eV[1], 1e3, 4)
        self.assertEqual(det.channels, 1000,)

    def testconvert_photondetector_opening(self):
        # Base options
        ops = Options(name="Test")
        ops.detectors['xray1'] = \
            PhotonIntensityDetector((radians(35), radians(45)), (0, radians(360.0)))
        ops.detectors['xray2'] = \
            PhotonIntensityDetector((radians(35), radians(45)), (0, radians(360.0)))
        ops.limits.add(TimeLimit(100))

        self.assertRaises(ConversionException, self.converter.convert, ops)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
