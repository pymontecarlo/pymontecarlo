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

from pymontecarlo.program.winxray.input.converter import Converter
from pymontecarlo.input.options import Options
from pymontecarlo.input.beam import PencilBeam
from pymontecarlo.input.detector import \
    (BackscatteredElectronEnergyDetector, PhotonSpectrumDetector, PhotonDepthDetector,
     PhotonIntensityDetector, TransmittedElectronEnergyDetector)
from pymontecarlo.input.limit import ShowersLimit, TimeLimit
from pymontecarlo.input.model import RANDOM_NUMBER_GENERATOR, ModelType

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
            opss = self.converter.convert(ops)

        # Test
        self.assertEqual(1, len(opss))

        # 6 warnings for the default models
        self.assertEqual(6, len(ws))

        self.assertAlmostEqual(1234, opss[0].beam.energy_eV, 4)

        self.assertEqual(1, len(opss[0].detectors))
        det = opss[0].detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(opss[0].limits))
        limit = list(opss[0].limits.iterclass(ShowersLimit))[0]
        self.assertEqual(5678, limit.showers)

        self.assertEqual(7, len(opss[0].models))
        model = list(opss[0].models.iterclass(RANDOM_NUMBER_GENERATOR))[0]
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
            opss = self.converter.convert(ops)

        # Test
        self.assertEqual(1, len(opss))

        # 10 warnings:
        # PencilBeam -> GaussianBeam (1)
        # Remove TransmittedElectronEnergyDetector (1)
        # Remove TimeLimit (1)
        # Set default models (7)
        self.assertEqual(10, len(ws))

        self.assertAlmostEqual(1234, opss[0].beam.energy_eV, 4)

        self.assertEqual(1, len(opss[0].detectors))
        det = opss[0].detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(opss[0].limits))
        limit = list(opss[0].limits.iterclass(ShowersLimit))[0]
        self.assertEqual(5678, limit.showers)

        self.assertEqual(7, len(opss[0].models))

    def testconvert3(self):
        # Base options
        ops = Options(name="Test")
        ops.beam.energy_eV = 100e3
        ops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        ops.detectors['bse2'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        ops.limits.add(ShowersLimit(5678))

        # Convert
        opss = self.converter.convert(ops)

        # Test
        self.assertEqual(2, len(opss))

    def testconvert4(self):
        # Base options
        ops = Options(name="Test")
        ops.beam.energy = 100e3
        ops.detectors['prz'] = PhotonDepthDetector((0, 1), (2, 3), 1000)
        ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))
        ops.limits.add(ShowersLimit(5678))

        # Convert
        opss = self.converter.convert(ops)

        # Test
        self.assertEqual(1, len(opss))
        self.assertEqual(2, len(opss[0].detectors))
        self.assertEqual(7, len(opss[0].models))

        # Test difference in elevation
        ops.detectors['xray'] = PhotonIntensityDetector((0.5, 1), (2, 3))
        opss = self.converter.convert(ops)
        self.assertEqual(2, len(opss))

        # Test difference in azimuth
        ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2.5, 3))
        opss = self.converter.convert(ops)
        self.assertEqual(2, len(opss))

        # Test difference in elevation (PhotonSpectrumDetector)
        ops.detectors['xray'] = PhotonSpectrumDetector((0.5, 1), (2, 3), (0, 1234), 1000)
        opss = self.converter.convert(ops)
        self.assertEqual(2, len(opss))
#
    def testconvert6(self):
        NEW_MODEL_TYPE = ModelType('new')
        NEW_MODEL_TYPE.test = ('test',)

        # Base options
        ops = Options(name="Test")
        ops.beam.energy_eV = 100e3
        ops.detectors['prz'] = PhotonDepthDetector((0, 1), (2, 3), 1000)
        ops.models.add(NEW_MODEL_TYPE.test)
        ops.limits.add(ShowersLimit(5678))

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            opss = self.converter.convert(ops)

        # Test
        self.assertEqual(1, len(opss))
        self.assertEqual(8, len(ws))
#
    def testconvert7(self):
        # Base options
        ops = Options(name="Test")
        ops.beam.energy_eV = 100e3
        ops.detectors['prz'] = PhotonDepthDetector((0, 1), (2, 3), 1000)

        # Convert
        opss = self.converter.convert(ops)

        # No shower limit
        self.assertEqual(0, len(opss))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
