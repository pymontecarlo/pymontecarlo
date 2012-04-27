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

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.program.casino2.io.importer import Importer
from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import \
    PhotonIntensityDetector, ElectronFractionDetector

import DrixUtilities.Files as Files

# Globals and constants variables.

class TestCasino2Importer(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.ops = Options()
        self.ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))
        self.ops.detectors['fraction'] = ElectronFractionDetector()

        filepath = Files.getCurrentModulePath(__file__, '../testdata/result1.cas')
        imp = Importer()
        with open(filepath, 'rb') as f:
            self.results = imp.import_from_cas(self.ops, f)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEquals(self.ops, self.results.options)

    def test_detector_photon_intensity(self):
        self.assertTrue('xray' in self.results)

        result = self.results['xray']
        self.assertEqual(self.ops.detectors['xray'], result.detector)

        val, unc = result.intensity('Au MV')
        self.assertAlmostEqual(2.57490804844e-06, val, 10)
        self.assertAlmostEqual(0.0, unc, 4)

    def test_detector_electron_fraction(self):
        self.assertTrue('fraction' in self.results)

        result = self.results['fraction']
        self.assertEqual(self.ops.detectors['fraction'], result.detector)

        val, unc = result.backscattered
        self.assertAlmostEqual(0.017436, val, 5)
        self.assertAlmostEqual(0.0, unc, 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.ERROR)
    unittest.main()
