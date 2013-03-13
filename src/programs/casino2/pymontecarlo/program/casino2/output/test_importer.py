#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.program.casino2.output.importer import Importer
from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import \
    (PhotonIntensityDetector, ElectronFractionDetector,
     PhotonDepthDetector, PhotonRadialDetector)

# Globals and constants variables.

class TestCasino2Importer(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.ops = Options()
        self.ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))
        self.ops.detectors['fraction'] = ElectronFractionDetector()
        self.ops.detectors['photondepth'] = PhotonDepthDetector((0, 1), (2, 3), 500)
        self.ops.detectors['photonradial'] = PhotonRadialDetector((0, 1), (2, 3), 500)

        filepath = os.path.join(os.path.dirname(__file__),
                                '../testdata/result1.cas')
        imp = Importer()
        with open(filepath, 'rb') as f:
            self.results = imp.import_from_cas(self.ops, f)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test_detector_photon_intensity(self):
        self.assertTrue('xray' in self.results)

        result = self.results['xray']

        val, unc = result.intensity('Au MV')
        self.assertAlmostEqual(2.57490804844e-06, val, 10)
        self.assertAlmostEqual(0.0, unc, 4)

    def test_detector_electron_fraction(self):
        self.assertTrue('fraction' in self.results)

        result = self.results['fraction']

        val, unc = result.backscattered
        self.assertAlmostEqual(0.017436, val, 5)
        self.assertAlmostEqual(0.0, unc, 4)

    def test_detector_photondepth(self):
        self.assertTrue('photondepth' in self.results)

        result = self.results['photondepth']

        self.assertEqual(11, len(list(result.iter_transitions())))

        pz = result.get('Au MV')
        self.assertEqual(499, len(pz[:, 0]))
        self.assertAlmostEqual(0.0, pz[-1, 0], 9)
        self.assertAlmostEqual(-1.425e-7, pz[0, 0], 9)
        self.assertAlmostEqual(1.0019390, pz[-1, 1], 4)
        self.assertAlmostEqual(0.0, pz[0, 1], 4)

    def test_detector_photonradial(self):
        self.assertTrue('photonradial' in self.results)

        result = self.results['photonradial']

        self.assertEqual(11, len(list(result.iter_transitions())))

        pr = result.get('Zn LIII')
        self.assertEqual(499, len(pr[:, 0]))
        self.assertAlmostEqual(1.422144e-7, pr[-1, 0], 9)
        self.assertAlmostEqual(0.0, pr[0, 0], 9)
        self.assertAlmostEqual(0.00011869, pr[-1, 1] / 1e18, 4)
        self.assertAlmostEqual(188.53822, pr[0, 1] / 1e18, 4)

if __name__ == '__main__':  #pragma: no cover
    logging.getLogger().setLevel(logging.ERROR)
    unittest.main()
