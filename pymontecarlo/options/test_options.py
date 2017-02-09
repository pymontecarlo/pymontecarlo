#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.limit import ShowersLimit, UncertaintyLimit
from pymontecarlo.options.model import ElasticCrossSectionModel, EnergyLossModel

# Globals and constants variables.

class TestOptions(TestCase):

    def setUp(self):
        super().setUp()

        self.options = self.create_basic_options()

    def testskeleton(self):
        self.assertAlmostEqual(15e3, self.options.beam.energy_eV, 4)

    def testcreate_datarow(self):
        datarow = set(self.options.create_datarow().items())
        self.assertEqual(14, len(datarow))

        options = self.create_basic_options()
        options.beam.energy_eV = 14e3
        other_datarow = set(options.create_datarow().items())
        diff = datarow ^ other_datarow
        self.assertEqual(2, len(diff))

    def testfind_detectors(self):
        detectors = self.options.find_detectors(PhotonDetector)
        self.assertEqual(1, len(detectors))

        detectors = self.options.find_detectors(object)
        self.assertEqual(0, len(detectors))

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

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
