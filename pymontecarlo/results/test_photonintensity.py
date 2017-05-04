#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResultBuilder
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.

class TestEmittedPhotonIntensityResult(TestCase):

    def setUp(self):
        super().setUp()

        detector = PhotonDetector(1.1, 2.2)
        analysis = PhotonIntensityAnalysis(detector)
        b = EmittedPhotonIntensityResultBuilder(analysis)
        b.add_intensity((13, 'Ka1'), 1.0, 0.1)
        b.add_intensity((13, 'Ka2'), 2.0, 0.2)
        b.add_intensity((13, 'Kb1'), 4.0, 0.5)
        b.add_intensity((13, 'Kb3'), 5.0, 0.7)
        b.add_intensity((13, 'Ll'), 3.0, 0.1)
        self.r = b.build()

    def testget(self):
        q = self.r.get((13, 'Ka1'))
        self.assertAlmostEqual(1.0, q.n, 4)
        self.assertAlmostEqual(0.1, q.s, 4)

        q = self.r.get((14, 'Ka1'))
        self.assertAlmostEqual(0.0, q.n, 4)
        self.assertAlmostEqual(0.0, q.s, 4)

        q = self.r.get((14, 'Ka1'), None)
        self.assertIsNone(q)

class TestEmittedPhotonIntensityResultBuilder(TestCase):

    def setUp(self):
        super().setUp()

        detector = PhotonDetector(1.1, 2.2)
        analysis = PhotonIntensityAnalysis(detector)
        self.b = EmittedPhotonIntensityResultBuilder(analysis)

    def testbuild(self):
        self.b.add_intensity((13, 'Ka1'), 1.0, 0.1)
        self.b.add_intensity((13, 'Ka2'), 2.0, 0.2)
        self.b.add_intensity((13, 'Kb1'), 4.0, 0.5)
        self.b.add_intensity((13, 'Kb3'), 5.0, 0.7)
        self.b.add_intensity((13, 'Ll'), 3.0, 0.1)
        result = self.b.build()

        self.assertEqual(5, len(result))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
