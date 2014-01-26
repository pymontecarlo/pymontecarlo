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
import os
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import \
    (PhotonSpectrumDetector,
     PhotonIntensityDetector,
     PhotonDepthDetector,
     ElectronFractionDetector,
     TimeDetector,
     ShowersStatisticsDetector,
     BackscatteredElectronEnergyDetector)
from pymontecarlo.program.penepma.importer import Importer

# Globals and constants variables.

class TestImporter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.testdata = os.path.join(os.path.dirname(__file__),
                                     'testdata', 'test1')

        self.i = Importer()

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test_detector_photon_intensity(self):
        # Create
        ops = Options(name='test1')
        ops.beam.energy_eV = 20e3
        ops.detectors['xray1'] = \
            PhotonIntensityDetector((radians(35), radians(45)), (0, radians(360.0)))
        ops.detectors['xray2'] = \
            PhotonIntensityDetector((radians(-45), radians(-35)), (0, radians(360.0)))

        # Import
        results = self.i.import_(ops, self.testdata)[0]

        # Test
        self.assertEqual(2, len(results))

        result = results['xray2']

        val, unc = result.intensity('W Ma1')
        self.assertAlmostEqual(6.07152e-05, val, 9)
        self.assertAlmostEqual(2.23e-06, unc, 9)

        val, unc = result.intensity('W Ma1', fluorescence=False)
        self.assertAlmostEqual(5.437632e-05, val, 9)
        self.assertAlmostEqual(2.12e-06, unc, 9)

        val, unc = result.intensity('W Ma1', absorption=False)
        self.assertAlmostEqual(5.521557e-4, val, 9)
        self.assertAlmostEqual(4.79e-06, unc, 9)

        val, unc = result.intensity('W Ma1', absorption=False, fluorescence=False)
        self.assertAlmostEqual(4.883132e-4, val, 9)
        self.assertAlmostEqual(4.45e-06, unc, 9)

    def test_detector_photon_spectrum(self):
        # Create
        ops = Options(name='test1')
        ops.beam.energy_eV = 20e3
        ops.detectors['spectrum'] = \
            PhotonSpectrumDetector((radians(35), radians(45)), (0, radians(360.0)),
                                   1000, (0, 20e3))

        # Import
        results = self.i.import_(ops, self.testdata)[0]

        # Test
        self.assertEqual(1, len(results))

        result = results['spectrum']

        total = result.get_total()
        self.assertEqual(1000, len(total))
        self.assertAlmostEqual(10.0, total[0, 0], 4)
        self.assertAlmostEqual(19990.0, total[-1, 0], 4)
        self.assertAlmostEqual(2.841637e-6, total[31, 1], 10)
        self.assertAlmostEqual(8.402574e-6, total[31, 2], 10)

        background = result.get_background()
        self.assertEqual(1000, len(background))
        self.assertAlmostEqual(10.0, background[0, 0], 4)
        self.assertAlmostEqual(19990.0, background[-1, 0], 4)
        self.assertAlmostEqual(4.0148e-8, background[31, 1], 10)
        self.assertAlmostEqual(1.6802574e-5, background[31, 2], 10)

    def test_detector_phirhoz(self):
        # Create
        ops = Options(name='test1')
        ops.beam.energy_eV = 20e3
        ops.detectors['prz'] = \
            PhotonDepthDetector((radians(35), radians(45)), (0, radians(360.0)), 500)

        # Import
        results = self.i.import_(ops, self.testdata)[0]

        # Test
        self.assertEqual(1, len(results))

        result = results['prz']

        self.assertTrue(result.exists('Al Ka1'))
        self.assertTrue(result.exists('Fe Ka1'))

        prz = result.get('Al Ka1')
        self.assertEqual(249, len(prz))
        self.assertAlmostEqual(0.0, prz[-1, 0], 4)
        self.assertAlmostEqual(4.704016e-3, prz[-1, 1], 6)
        self.assertAlmostEqual(7.06e-3, prz[-1, 2], 6)

        prz = result.get('Al Ka1', absorption=False)
        self.assertEqual(249, len(prz))
        self.assertAlmostEqual(0.0, prz[-1, 0], 4)
        self.assertAlmostEqual(3.910867e-3, prz[-1, 1], 6)
        self.assertAlmostEqual(2.35e-3, prz[-1, 2], 6)

        prz = result.get('Al Ka1', fluorescence=False)
        self.assertEqual(249, len(prz))
        self.assertAlmostEqual(0.0, prz[-1, 0], 4)
        self.assertAlmostEqual(1.353710, prz[-1, 1], 6)
        self.assertAlmostEqual(3.63e+1, prz[-1, 2], 6)

        prz = result.get('Al Ka1', absorption=False, fluorescence=False)
        self.assertEqual(249, len(prz))
        self.assertAlmostEqual(0.0, prz[-1, 0], 4)
        self.assertAlmostEqual(1.764721, prz[-1, 1], 6)
        self.assertAlmostEqual(7.56e-1, prz[-1, 2], 6)

    def test_detector_electron_fraction(self):
        # Create
        ops = Options(name='test1')
        ops.beam.energy_eV = 20e3
        ops.detectors['fraction'] = ElectronFractionDetector()

        # Import
        results = self.i.import_(ops, self.testdata)[0]

        # Test
        self.assertEqual(1, len(results))

        result = results['fraction']

        self.assertAlmostEqual(0.2336, result.backscattered[0], 4)
        self.assertAlmostEqual(0.6713e-2, result.backscattered[1], 6)

        self.assertAlmostEqual(0.0, result.transmitted[0], 4)
        self.assertAlmostEqual(0.0, result.transmitted[1], 4)

        self.assertAlmostEqual(0.7759, result.absorbed[0], 4)
        self.assertAlmostEqual(0.5447e-2, result.absorbed[1], 6)

    def test_detector_time(self):
        # Create
        ops = Options(name='test1')
        ops.beam.energy_eV = 20e3
        ops.detectors['time'] = TimeDetector()

        # Import
        results = self.i.import_(ops, self.testdata)[0]

        # Test
        self.assertEqual(1, len(results))

        result = results['time']

        self.assertAlmostEqual(0.3495e3, result.simulation_time_s, 4)
        self.assertAlmostEqual(1.0 / 0.1508e3, result.simulation_speed_s[0], 4)

    def test_detector_showers_statistics(self):
        # Create
        ops = Options(name='test1')
        ops.beam.energy_eV = 20e3
        ops.detectors['showers'] = ShowersStatisticsDetector()

        # Import
        results = self.i.import_(ops, self.testdata)[0]

        # Test
        self.assertEqual(1, len(results))

        result = results['showers']

        self.assertEqual(52730, result.showers)

    def test_detector_backscattered_electron_energy(self):
        # Create
        ops = Options(name='test1')
        ops.beam.energy_eV = 20e3
        ops.detectors['bse'] = \
            BackscatteredElectronEnergyDetector(100, (0.0, 20e3))

        # Import
        results = self.i.import_(ops, self.testdata)[0]

        # Test
        self.assertEqual(1, len(results))

        result = results['bse']

        self.assertEqual(250, len(result))


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
