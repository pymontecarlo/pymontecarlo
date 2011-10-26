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
from pymontecarlo.input.casino2.converter import Casino2Converter, ConversionException
from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.beam import PencilBeam
from pymontecarlo.input.base.detector import \
    (BackscatteredElectronEnergyDetector, PhotonSpectrumDetector, PhiRhoZDetector,
     PhotonIntensityDetector)
from pymontecarlo.input.base.limit import ShowersLimit, TimeLimit

# Globals and constants variables.

class TestCasino2Converter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.converter = Casino2Converter()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testconvert1(self):
        # Base options
        baseops = Options(name="Test")
        baseops.beam.energy = 1234
        baseops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        baseops.limits.add(ShowersLimit(5678))

        # Convert
        ops = self.converter.convert(baseops)

        # Test
        self.assertAlmostEqual(1234, ops.beam.energy, 4)

        self.assertEqual(1, len(ops.detectors))
        det = ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits[0], 4)
        self.assertAlmostEqual(1234, det.limits[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(ops.limits))
        limit = ops.limits.find(ShowersLimit)
        self.assertEqual(5678, limit.showers)

    def testconvert2(self):
        # Base options
        baseops = Options(name="Test")
        baseops.beam = PencilBeam(1234)
        baseops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        baseops.detectors['photon'] = \
            PhotonSpectrumDetector((radians(35), radians(45)), (0, radians(360.0)),
                                   (12.34, 56.78), 1000)
        baseops.limits.add(ShowersLimit(5678))
        baseops.limits.add(TimeLimit(60))

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            ops = self.converter.convert(baseops)

        # 3 warnings:
        # PencilBeam -> GaussianBeam
        # Remove PhotonSpectrumDetector
        # Remove TimeLimit
        self.assertEqual(3, len(ws))

        # Test
        self.assertAlmostEqual(1234, ops.beam.energy, 4)

        self.assertEqual(1, len(ops.detectors))
        det = ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits[0], 4)
        self.assertAlmostEqual(1234, det.limits[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(ops.limits))
        limit = ops.limits.find(ShowersLimit)
        self.assertEqual(5678, limit.showers)

    def testconvert3(self):
        # Base options
        baseops = Options(name="Test")
        baseops.beam.energy = 100e3
        baseops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        baseops.detectors['bse2'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)

        # Two many BackscatteredElectronEnergyDetector
        self.assertRaises(ConversionException, self.converter.convert, baseops)

    def testconvert4(self):
        # Base options
        baseops = Options(name="Test")
        baseops.beam.energy = 100e3
        baseops.detectors['prz'] = PhiRhoZDetector((0, 1), (2, 3), (0, -10), 1000)
        baseops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))

        # Convert
        ops = self.converter.convert(baseops)

        self.assertEqual(2, len(ops.detectors))

        # Test difference in elevation
        baseops.detectors['xray'] = PhotonIntensityDetector((0.5, 1), (2, 3))
        self.assertRaises(ConversionException, self.converter.convert, baseops)

        # Test difference in azimuth
        baseops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2.5, 3))
        self.assertRaises(ConversionException, self.converter.convert, baseops)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
