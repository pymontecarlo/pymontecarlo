#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis.photonintensity import \
    PhotonIntensityAnalysis, PhotonIntensityAnalysisBuilder
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResult

# Globals and constants variables.

class TestPhotonIntensityAnalysis(TestCase):

    def setUp(self):
        super().setUp()

        det = PhotonDetector('det', math.radians(40.0))
        self.a = PhotonIntensityAnalysis(det)

        self.options = self.create_basic_options()

    def testapply(self):
        list_options = self.a.apply(self.options)
        self.assertEqual(0, len(list_options))

    def testcalculate(self):
        simulation = self.create_basic_simulation()
        result = simulation.find_result(EmittedPhotonIntensityResult)[0]
        self.assertEqual(7, len(result))

        newresult = self.a.calculate(simulation, [simulation])

        self.assertTrue(newresult)
        self.assertEqual(10, len(result))

        q = result[(29, 'Ka')]
        self.assertAlmostEqual(3.0, q.n, 4)
        self.assertAlmostEqual(0.2236, q.s, 4)

        q = result[(29, 'Kb')]
        self.assertAlmostEqual(10.5, q.n, 4)
        self.assertAlmostEqual(0.8718, q.s, 4)

        q = result[(29, 'K')]
        self.assertAlmostEqual(13.5, q.n, 4)
        self.assertAlmostEqual(0.9, q.s, 4)

        newresult = self.a.calculate(simulation, [simulation])
        self.assertFalse(newresult)

        # Just to make sure
        newresult = self.a.calculate(simulation, [simulation])
        self.assertFalse(newresult)

class TestPhotonIntensityAnalysisBuilder(TestCase):

    def testbuild(self):
        b = PhotonIntensityAnalysisBuilder()
        self.assertEqual(0, len(b))
        self.assertEqual(0, len(b.build()))

    def testbuild2(self):
        b = PhotonIntensityAnalysisBuilder()
        b.add_photon_detector(self.create_basic_photondetector())
        b.add_photon_detector(self.create_basic_photondetector())
        self.assertEqual(1, len(b))
        self.assertEqual(1, len(b.build()))

    def testbuild3(self):
        b = PhotonIntensityAnalysisBuilder()
        b.add_photon_detector(self.create_basic_photondetector())
        d2 = self.create_basic_photondetector()
        d2.elevation_deg = 0.1
        b.add_photon_detector(d2)
        self.assertEqual(2, len(b))
        self.assertEqual(2, len(b.build()))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
