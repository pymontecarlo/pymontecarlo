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

# Third party modules.

# Local modules.
from pymontecarlo.program.winxray.io.importer import Importer
from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import \
    PhotonIntensityDetector, ElectronFractionDetector, TimeDetector

import DrixUtilities.Files as Files


# Globals and constants variables.

class TestImporter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options()
        self.ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))
        self.ops.detectors['fraction'] = ElectronFractionDetector()
        self.ops.detectors['time'] = TimeDetector()

        dirpath = Files.getCurrentModulePath(__file__, '../testdata/al_10keV_1ke_001')
        self.results = Importer().import_from_dir(self.ops, dirpath)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test_detector_photon_intensity(self):
        result = self.results['xray']

        val, unc = result.intensity('Al Ka1')
        self.assertAlmostEqual(276142, val, 3)
        self.assertAlmostEqual(1668.34, unc, 3)

        val, unc = result.intensity('Al Ka1', absorption=False)
        self.assertAlmostEqual(294642, val, 3)
        self.assertAlmostEqual(1833.41, unc, 3)

    def test_detector_electron_fraction(self):
        result = self.results['fraction']
        self.assertAlmostEqual(0.152, result.backscattered[0], 3)
        self.assertAlmostEqual(0.0340597, result.backscattered[1], 3)

    def test_detector_time(self):
        result = self.results['time']
        self.assertAlmostEqual(64.486, result.simulation_time_s, 3)
        self.assertAlmostEqual(0.064486, result.simulation_speed_s[0], 3)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
