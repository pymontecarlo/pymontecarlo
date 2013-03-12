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

from pymontecarlo.program.winxray.input.converter import Converter, ConversionException
from pymontecarlo.input.options import Options
from pymontecarlo.input.beam import PencilBeam
from pymontecarlo.input.detector import \
    (BackscatteredElectronEnergyDetector, PhotonSpectrumDetector, PhotonDepthDetector,
     PhotonIntensityDetector, TransmittedElectronEnergyDetector)
from pymontecarlo.input.limit import ShowersLimit, TimeLimit
from pymontecarlo.input.model import \
    RANDOM_NUMBER_GENERATOR, ModelType, ModelCategory, Model

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
        ops = Options(name="Test")
        ops.beam.energy_eV = 1234
        ops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        ops.limits.add(ShowersLimit(5678))
        ops.models.add(RANDOM_NUMBER_GENERATOR.press1966_rand1)

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            self.converter.convert(ops)

        # 6 warnings for the default models
        self.assertEqual(6, len(ws))

        # Test
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)

        self.assertEqual(1, len(ops.detectors))
        det = ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(ops.limits))
        limit = ops.limits.find(ShowersLimit)
        self.assertEqual(5678, limit.showers)

        self.assertEqual(7, len(ops.models))
        model = ops.models.find(RANDOM_NUMBER_GENERATOR.type)
        self.assertEqual(RANDOM_NUMBER_GENERATOR.press1966_rand1, model)

    def testconvert2(self):
        # Base options
        ops = Options(name="Test")
        ops.beam = PencilBeam(1234)
        ops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        ops.detectors['photon'] = TransmittedElectronEnergyDetector((0, 1234), 1000)
        ops.limits.add(ShowersLimit(5678))
        ops.limits.add(TimeLimit(60))

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            self.converter.convert(ops)

        # 10 warnings:
        # PencilBeam -> GaussianBeam (1)
        # Remove TransmittedElectronEnergyDetector (1)
        # Remove TimeLimit (1)
        # Set default models (7)
        self.assertEqual(10, len(ws))

        # Test
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)

        self.assertEqual(1, len(ops.detectors))
        det = ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(ops.limits))
        limit = ops.limits.find(ShowersLimit)
        self.assertEqual(5678, limit.showers)

        self.assertEqual(7, len(ops.models))

    def testconvert3(self):
        # Base options
        ops = Options(name="Test")
        ops.beam.energy_eV = 100e3
        ops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        ops.detectors['bse2'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        ops.limits.add(ShowersLimit(5678))

        # Two many BackscatteredElectronEnergyDetector
        self.assertRaises(ConversionException, self.converter.convert, ops)

    def testconvert4(self):
        # Base options
        ops = Options(name="Test")
        ops.beam.energy = 100e3
        ops.detectors['prz'] = PhotonDepthDetector((0, 1), (2, 3), 1000)
        ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))
        ops.limits.add(ShowersLimit(5678))

        # Convert
        self.converter.convert(ops)

        self.assertEqual(2, len(ops.detectors))
        self.assertEqual(7, len(ops.models))

        # Test difference in elevation
        ops.detectors['xray'] = PhotonIntensityDetector((0.5, 1), (2, 3))
        self.assertRaises(ConversionException, self.converter.convert, ops)

        # Test difference in azimuth
        ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2.5, 3))
        self.assertRaises(ConversionException, self.converter.convert, ops)

        # Test difference in elevation (PhotonSpectrumDetector)
        ops.detectors['xray'] = PhotonSpectrumDetector((0.5, 1), (2, 3), (0, 1234), 1000)
        self.assertRaises(ConversionException, self.converter.convert, ops)

    def testconvert6(self):
        NEW_MODEL_TYPE = ModelType('new')
        NEW_MODEL_CATEGORY = ModelCategory(NEW_MODEL_TYPE)
        NEW_MODEL_CATEGORY.test = Model('test')

        # Base options
        ops = Options(name="Test")
        ops.beam.energy_eV = 100e3
        ops.models.add(NEW_MODEL_CATEGORY.test)
        ops.limits.add(ShowersLimit(5678))

        with warnings.catch_warnings(record=True) as ws:
            self.converter.convert(ops)

        self.assertEqual(8, len(ws))

    def testconvert7(self):
        # Base options
        ops = Options(name="Test")
        ops.beam.energy_eV = 100e3

        # No shower limit
        self.assertRaises(ConversionException, self.converter.convert, ops)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
