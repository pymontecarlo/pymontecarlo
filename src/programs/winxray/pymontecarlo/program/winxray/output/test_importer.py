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

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.program.winxray.output.importer import Importer
from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import \
    (PhotonIntensityDetector, PhotonDepthDetector, ElectronFractionDetector,
     TimeDetector, PhotonSpectrumDetector, ShowersStatisticsDetector)
from pymontecarlo.input.limit import ShowersLimit

# Globals and constants variables.

class TestImporter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.ops = Options()

        self.ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))
        self.ops.detectors['fraction'] = ElectronFractionDetector()
        self.ops.detectors['time'] = TimeDetector()
        self.ops.detectors['showers'] = ShowersStatisticsDetector()
        self.ops.detectors['prz'] = PhotonDepthDetector((0, 1), (2, 3), 100)
        self.ops.detectors['spectrum'] = \
            PhotonSpectrumDetector((0, 1), (2, 3), (0, 1000), 500)

        self.ops.limits.add(ShowersLimit(1000))

        dirpath = os.path.join(os.path.dirname(__file__),
                               '../testdata/al_10keV_1ke_001')
        self.results = Importer().import_(self.ops, dirpath)[0]

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test_detector_photon_intensity(self):
        result = self.results['xray']
        factor = 1000 * 0.459697694132 # Normalization

        val, unc = result.intensity('Al Ka1')
        self.assertAlmostEqual(276142 / factor, val, 3)
        self.assertAlmostEqual(1668.34 / factor, unc, 3)

        val, unc = result.intensity('Al Ka1', absorption=False)
        self.assertAlmostEqual(294642 / factor, val, 3)
        self.assertAlmostEqual(1833.41 / factor, unc, 3)

    def test_detector_electron_fraction(self):
        result = self.results['fraction']
        self.assertAlmostEqual(0.152, result.backscattered[0], 3)
        self.assertAlmostEqual(0.0340597, result.backscattered[1], 3)

    def test_detector_time(self):
        result = self.results['time']
        self.assertAlmostEqual(64.486, result.simulation_time_s, 3)
        self.assertAlmostEqual(0.064486, result.simulation_speed_s[0], 3)

    def test_detector_showers_statistics(self):
        result = self.results['showers']
        self.assertEqual(1000, result.showers)

    def test_detector_photondepth(self):
        result = self.results['prz']
        self.assertEqual(3, len(list(result.iter_transitions())))
        self.assertEqual(1, len(list(result.iter_transitions(absorption=False))))

        prz = result.get('Al Ka1')
        self.assertAlmostEqual(0.0, prz[0, 0], 4)
        self.assertAlmostEqual(1.3379, prz[0, 1], 4)
        self.assertAlmostEqual(0.03524, prz[0, 2], 4)

    def test_detector_photon_spectrum(self):
        result = self.results['spectrum']
        factor = 1000 * 0.459697694132 * 10.0 # Normalization

        self.assertAlmostEqual(10.0, result.energy_channel_width_eV, 4)
        self.assertAlmostEqual(5.0, result.energy_offset_eV, 4)

        # Total
        total = result.get_total()
        self.assertEqual(1000, len(total))
        self.assertAlmostEqual(1485, total[148, 0], 4)
        self.assertAlmostEqual(29489.1 / factor, total[148, 1], 4)
        self.assertAlmostEqual(0.0, total[148, 2], 4)

        # Background
        background = result.get_background()
        self.assertEqual(1000, len(background))
        self.assertAlmostEqual(1485, background[148, 0], 4)
        self.assertAlmostEqual(194.188 / factor, background[148, 1], 4)
        self.assertAlmostEqual(0.0, background[148, 2], 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
