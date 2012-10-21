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

from pymontecarlo.program.winxray.io.importer import Importer
from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import \
    (PhotonIntensityDetector, PhiRhoZDetector, ElectronFractionDetector,
     TimeDetector, PhotonSpectrumDetector)
from pymontecarlo.input.limit import ShowersLimit

# Globals and constants variables.

class TestImporter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.ops = Options()

        self.ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))
        self.ops.detectors['fraction'] = ElectronFractionDetector()
        self.ops.detectors['time'] = TimeDetector()
        self.ops.detectors['prz'] = PhiRhoZDetector((0, 1), (2, 3), 100)
        self.ops.detectors['spectrum'] = \
            PhotonSpectrumDetector((0, 1), (2, 3), (0, 1000), 500)

        self.ops.limits.add(ShowersLimit(1000))

        dirpath = os.path.join(os.path.dirname(__file__),
                               '../testdata/al_10keV_1ke_001')
        self.results = Importer().import_from_dir(self.ops, dirpath)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test_detector_photon_intensity(self):
        result = self.results['xray']
        factor = 1000 * 0.459697694132  # Normalization

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

    def test_detector_phirhoz(self):
        result = self.results['prz']
        self.assertEqual(3, len(list(result.iter_transitions())))
        self.assertEqual(1, len(list(result.iter_transitions(absorption=False))))

        rzs, vals, uncs = result.get('Al Ka1')
        self.assertAlmostEqual(0.0, rzs[0], 4)
        self.assertAlmostEqual(1.3379, vals[0], 4)
        self.assertAlmostEqual(0.03524, uncs[0], 4)

    def test_detector_photon_spectrum(self):
        result = self.results['spectrum']
        factor = 1000 * 0.459697694132 * 10.0  # Normalization

        self.assertAlmostEqual(10.0, result.energy_channel_width_eV, 4)
        self.assertAlmostEqual(0.0, result.energy_offset_eV, 4)

        # Total
        energies, vals, uncs = result.get_total()
        self.assertEqual(1000, len(energies))
        self.assertEqual(1000, len(vals))
        self.assertEqual(1000, len(uncs))

        self.assertAlmostEqual(1480, energies[148], 4)
        self.assertAlmostEqual(29489.1 / factor, vals[148], 4)
        self.assertAlmostEqual(0.0, uncs[148], 4)

        # Background
        energies, vals, uncs = result.get_background()
        self.assertEqual(1000, len(energies))
        self.assertEqual(1000, len(vals))
        self.assertEqual(1000, len(uncs))

        self.assertAlmostEqual(1480, energies[148], 4)
        self.assertAlmostEqual(194.188 / factor, vals[148], 4)
        self.assertAlmostEqual(0.0, uncs[148], 4)

if __name__ == '__main__':  #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
