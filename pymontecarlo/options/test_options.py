#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.detector.base import Detector
from pymontecarlo.options.options import OptionsBuilder
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.options.analysis.base import Analysis

# Globals and constants variables.

class TestOptions(TestCase):

    def setUp(self):
        super().setUp()

        self.options = self.create_basic_options()

    def testskeleton(self):
        self.assertAlmostEqual(15e3, self.options.beam.energy_eV, 4)

    def testfind_detectors(self):
        detectors = self.options.find_detectors(PhotonDetector)
        self.assertEqual(1, len(detectors))

        detectors = self.options.find_detectors(Detector)
        self.assertEqual(1, len(detectors))

    def testfind_analyses(self):
        analyses = self.options.find_analyses(PhotonIntensityAnalysis)
        self.assertEqual(1, len(analyses))

        analyses = self.options.find_analyses(Analysis)
        self.assertEqual(1, len(analyses))

        analyses = self.options.find_analyses(PhotonIntensityAnalysis, self.options.detectors[0])
        self.assertEqual(1, len(analyses))

        analyses = self.options.find_analyses(Detector)
        self.assertEqual(0, len(analyses))

class TestOptionsBuilder(TestCase):

    def testbuild(self):
        b = OptionsBuilder()
        b.add_program(self.create_basic_program())
        b.add_beam(self.create_basic_beam())
        b.add_sample(self.create_basic_sample())
        self.assertEqual(1, len(b))
        self.assertEqual(1, len(b.build()))

    def testbuild2(self):
        b = OptionsBuilder()
        b.add_program(self.create_basic_program())
        b.add_program(self.create_basic_program())
        b.add_beam(self.create_basic_beam())
        b.add_beam(self.create_basic_beam())
        b.add_sample(self.create_basic_sample())
        b.add_sample(self.create_basic_sample())
        self.assertEqual(1, len(b))
        self.assertEqual(1, len(b.build()))

    def testbuild3(self):
        b = OptionsBuilder()
        b.add_program(self.create_basic_program())
        b.add_beam(self.create_basic_beam())
        b.add_sample(self.create_basic_sample())

        det = self.create_basic_photondetector()
        b.add_analysis(KRatioAnalysis(det))

        self.assertEqual(2, len(b))
        self.assertEqual(2, len(b.build()))

    def testbuild4(self):
        b = OptionsBuilder()
        b.add_program(self.create_basic_program())
        b.add_beam(self.create_basic_beam())
        b.add_sample(self.create_basic_sample())

        det = self.create_basic_photondetector()
        b.add_analysis(KRatioAnalysis(det))
        b.add_analysis(PhotonIntensityAnalysis(det))

        self.assertEqual(2, len(b))
        self.assertEqual(2, len(b.build()))

    def testbuild5(self):
        b = OptionsBuilder()
        b.add_program(self.create_basic_program())
        b.add_beam(self.create_basic_beam())
        b.add_sample(self.create_basic_sample())

        det = self.create_basic_photondetector()
        b.add_analysis(KRatioAnalysis(det))

        det = PhotonDetector(3.3, 4.4)
        b.add_analysis(KRatioAnalysis(det))

        self.assertEqual(4, len(b))
        self.assertEqual(4, len(b.build()))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
