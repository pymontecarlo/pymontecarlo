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
from pymontecarlo.options.limit import ShowersLimit, UncertaintyLimit
from pymontecarlo.options.model import ElasticCrossSectionModel, EnergyLossModel
from pymontecarlo.options.options import OptionsBuilder
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis

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

    def testfind_limits(self):
        limits = self.options.find_limits(ShowersLimit)
        self.assertEqual(1, len(limits))

        limits = self.options.find_limits(UncertaintyLimit)
        self.assertEqual(0, len(limits))

    def testfind_models(self):
        models = self.options.find_models(ElasticCrossSectionModel)
        self.assertEqual(1, len(models))

        models = self.options.find_models(EnergyLossModel)
        self.assertEqual(0, len(models))

class TestOptionsBuilder(TestCase):

    def testbuild(self):
        b = OptionsBuilder()
        b.add_program(self.program)
        b.add_beam(self.create_basic_beam())
        b.add_sample(self.create_basic_sample())
        self.assertEqual(1, len(b))
        self.assertEqual(1, len(b.build()))

    def testbuild2(self):
        b = OptionsBuilder()
        b.add_program(self.program)
        b.add_program(self.program)
        b.add_beam(self.create_basic_beam())
        b.add_beam(self.create_basic_beam())
        b.add_sample(self.create_basic_sample())
        b.add_sample(self.create_basic_sample())
        self.assertEqual(1, len(b))
        self.assertEqual(1, len(b.build()))

    def testbuild3(self):
        b = OptionsBuilder()
        b.add_program(self.program)
        b.add_beam(self.create_basic_beam())
        b.add_sample(self.create_basic_sample())

        det = self.create_basic_photondetector()
        b.add_analysis(KRatioAnalysis(det))

        self.assertEqual(2, len(b))
        self.assertEqual(2, len(b.build()))

    def testbuild4(self):
        b = OptionsBuilder()
        b.add_program(self.program)
        b.add_beam(self.create_basic_beam())
        b.add_sample(self.create_basic_sample())

        det = self.create_basic_photondetector()
        b.add_analysis(KRatioAnalysis(det))
        b.add_analysis(PhotonIntensityAnalysis(det))

        self.assertEqual(2, len(b))
        self.assertEqual(2, len(b.build()))

    def testbuild5(self):
        b = OptionsBuilder()
        b.add_program(self.program)
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
