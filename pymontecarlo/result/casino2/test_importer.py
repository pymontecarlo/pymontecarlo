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
from pymontecarlo.result.casino2.importer import Casino2Importer
from pymontecarlo.input.casino2.options import Casino2Options
from pymontecarlo.input.base.detector import PhotonIntensityDetector

import DrixUtilities.Files as Files

# Globals and constants variables.

class TestCasino2Importer(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Casino2Options()
        self.ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))

        filepath = Files.getCurrentModulePath(__file__, '../../testdata/casino2/result1.cas')
        imp = Casino2Importer()
        self.results = imp.import_from_cas(self.ops, filepath)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEquals(self.ops, self.results.options)

    def test_detector_photon_intensity_detector(self):
        self.assertTrue('xray' in self.results)

        result = self.results['xray']
        self.assertEqual(self.ops.detectors['xray'], result.detector)

        val, unc = result.intensity('Au MV')
        self.assertAlmostEqual(2.57490804844e-06, val, 10)
        self.assertAlmostEqual(0.0, unc, 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.ERROR)
    unittest.main()
