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
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.program.casino2.importer import Importer
from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import \
    (PhotonIntensityDetector, ElectronFractionDetector,
     PhotonDepthDetector, PhotonRadialDetector,
     BackscatteredElectronEnergyDetector, TransmittedElectronEnergyDetector,
     BackscatteredElectronPolarAngularDetector,
     BackscatteredElectronRadialDetector, TrajectoryDetector)

# Globals and constants variables.

class TestCasino2Importer(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.ops = Options()
        self.ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))
        self.ops.detectors['fraction'] = ElectronFractionDetector()
        self.ops.detectors['photondepth'] = PhotonDepthDetector((0, 1), (2, 3), 500)
        self.ops.detectors['photonradial'] = PhotonRadialDetector((0, 1), (2, 3), 500)
        self.ops.detectors['bseenergy'] = BackscatteredElectronEnergyDetector(500, (0, 30e3))
        self.ops.detectors['teenergy'] = TransmittedElectronEnergyDetector(500, (0, 30e3))
        self.ops.detectors['bseangle'] = BackscatteredElectronPolarAngularDetector(91)
        self.ops.detectors['bseradial'] = BackscatteredElectronRadialDetector(500)
        self.ops.detectors['trajs'] = TrajectoryDetector()

        filepath = os.path.join(os.path.dirname(__file__),
                                'testdata', 'result1.cas')
        imp = Importer()
        with open(filepath, 'rb') as f:
            self.results = imp.import_cas(self.ops, f)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_detector_photon_intensity(self):
        self.assertIn('xray', self.results)

        result = self.results['xray']

        val, unc = result.intensity('Au MV')
        self.assertAlmostEqual(2.57490804844e-06, val, 10)
        self.assertAlmostEqual(0.0, unc, 4)

    def test_detector_electron_fraction(self):
        self.assertIn('fraction', self.results)

        result = self.results['fraction']

        val, unc = result.backscattered
        self.assertAlmostEqual(0.017436, val, 5)
        self.assertAlmostEqual(0.0, unc, 4)

    def test_detector_photondepth(self):
        self.assertIn('photondepth', self.results)

        result = self.results['photondepth']

        self.assertEqual(11, len(list(result.iter_transitions())))

        pz = result.get('Au MV')
        self.assertEqual(499, len(pz[:, 0]))
        self.assertAlmostEqual(0.0, pz[-1, 0], 9)
        self.assertAlmostEqual(-1.425e-7, pz[0, 0], 9)
        self.assertAlmostEqual(1.0019390, pz[-1, 1], 4)
        self.assertAlmostEqual(0.0, pz[0, 1], 4)

    def test_detector_photonradial(self):
        self.assertIn('photonradial', self.results)

        result = self.results['photonradial']

        self.assertEqual(11, len(list(result.iter_transitions())))

        pr = result.get('Zn LIII')
        self.assertEqual(499, len(pr[:, 0]))
        self.assertAlmostEqual(1.422144e-7, pr[-1, 0], 9)
        self.assertAlmostEqual(0.0, pr[0, 0], 9)
        self.assertAlmostEqual(0.00011869, pr[-1, 1] / 1e18, 4)
        self.assertAlmostEqual(188.53822, pr[0, 1] / 1e18, 4)

    def test_detector_backscattered_electron_energy(self):
        self.assertIn('bseenergy', self.results)

        result = self.results['bseenergy']

        data = result.get_data()
        self.assertEqual(500, len(data))
        self.assertAlmostEqual(0.0, data[0, 0], 4)
        self.assertAlmostEqual(30e3, data[-1, 0], 4)
        self.assertAlmostEqual(0.0, data[0, 1], 4)
        self.assertAlmostEqual(0.0404, data[-2, 1], 4)

    def test_detector_transmitted_electron_energy(self):
        self.assertIn('teenergy', self.results)

        result = self.results['teenergy']

        data = result.get_data()
        self.assertEqual(500, len(data))
        self.assertAlmostEqual(0.0, data[0, 0], 4)
        self.assertAlmostEqual(30e3, data[-1, 0], 4)
        self.assertAlmostEqual(0.0, data[0, 1], 4)
        self.assertAlmostEqual(0.89032, data[-7, 1], 4)

    def test_detector_backscattered_electron_polar_angular(self):
        self.assertIn('bseangle', self.results)

        result = self.results['bseangle']

        data = result.get_data()
        self.assertEqual(91, len(data))
        self.assertAlmostEqual(0.0, data[0, 0], 4)
        self.assertAlmostEqual(math.radians(90.0), data[-1, 0], 4)
        self.assertAlmostEqual(0.02020, data[-5, 1], 4)

    def test_detector_backscattered_electron_radial(self):
        self.assertIn('bseradial', self.results)

        result = self.results['bseradial']

        data = result.get_data()
        self.assertEqual(500, len(data))
        self.assertAlmostEqual(0.0, data[0, 0], 4)
        self.assertAlmostEqual(2.3904e-7, data[-1, 0], 10)
        self.assertAlmostEqual(14166675603221.422, data[-5, 1], 1)

    def test_detector_trajectory(self):
        self.assertIn('trajs', self.results)

        result = self.results['trajs']

        self.assertEqual(221, len(result))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.ERROR)
    unittest.main()
