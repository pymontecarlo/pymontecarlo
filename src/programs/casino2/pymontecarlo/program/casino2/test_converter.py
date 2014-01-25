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
from pymontecarlo.options.beam import PencilBeam
from pymontecarlo.options.detector import \
    (BackscatteredElectronEnergyDetector, PhotonSpectrumDetector,
     PhotonDepthDetector, PhotonIntensityDetector)
from pymontecarlo.options.limit import ShowersLimit, TimeLimit
from pymontecarlo.options.model import IONIZATION_CROSS_SECTION, ModelType

from pymontecarlo.program.casino2.converter import Converter

# Globals and constants variables.

class TestCasino2Converter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.converter = Converter()

    def tearDown(self):
        TestCase.tearDown(self)

    def testconvert1(self):
        # Base options
        ops = Options(name="Test")
        ops.beam.energy_eV = 1234
        ops.detectors['bse'] = BackscatteredElectronEnergyDetector(1000, (0, 1234))
        ops.limits.add(ShowersLimit(5678))
        ops.models.add(IONIZATION_CROSS_SECTION.jakoby)

        # Convert
        opss = self.converter.convert(ops)

        # Test
        self.assertEqual(1, len(opss))

        self.assertAlmostEqual(1234, opss[0].beam.energy_eV, 4)

        self.assertEqual(1, len(opss[0].detectors))
        det = ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(opss[0].limits))
        limit = list(ops.limits.iterclass(ShowersLimit))[0]
        self.assertEqual(5678, limit.showers)

        self.assertEqual(7, len(opss[0].models))
        model = list(ops.models.iterclass(IONIZATION_CROSS_SECTION))[0]
        self.assertEqual(IONIZATION_CROSS_SECTION.jakoby, model)

    def testconvert2(self):
        # Base options
        ops = Options(name="Test")
        ops.beam = PencilBeam(1234)
        ops.detectors['bse'] = BackscatteredElectronEnergyDetector(1000, (0, 1234))
        ops.detectors['photon'] = \
            PhotonSpectrumDetector((radians(35), radians(45)), (0, radians(360.0)),
                                   1000, (12.34, 56.78))
        ops.limits.add(ShowersLimit(5678))
        ops.limits.add(TimeLimit(60))

        # Convert
        opss = self.converter.convert(ops)

        # Test
        self.assertEqual(1, len(opss))

        self.assertAlmostEqual(1234, opss[0].beam.energy_eV, 4)

        self.assertEqual(1, len(opss[0].detectors))
        det = ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(opss[0].limits))
        limit = list(ops.limits.iterclass(ShowersLimit))[0]
        self.assertEqual(5678, limit.showers)

        self.assertEqual(7, len(opss[0].models))

    def testconvert3(self):
        # Base options
        ops = Options(name="Test")
        ops.beam.energy_eV = 100e3
        ops.detectors['bse'] = BackscatteredElectronEnergyDetector(1000, (0, 1234))
        ops.detectors['bse2'] = BackscatteredElectronEnergyDetector(1000, (0, 1234))
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

    def testconvert6(self):
        NEW_MODEL_TYPE = ModelType('new')
        NEW_MODEL_TYPE.test = ('test',)

        # Base options
        ops = Options(name="Test")
        ops.beam.energy_eV = 100e3
        ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))
        ops.models.add(NEW_MODEL_TYPE.test)
        ops.limits.add(ShowersLimit(5678))

        # Convert
        opss = self.converter.convert(ops)

        self.assertEqual(1, len(opss))

    def testconvert7(self):
        # Base options
        ops = Options(name="Test")
        ops.beam.energy_eV = 100e3

        # Convert
        opss = self.converter.convert(ops)

        # Test
        self.assertEqual(0, len(opss)) # No shower limit

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
