#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.analyses.kratio import KRatioAnalysis
from pymontecarlo.options.analyses.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestKRatioAnalysis(TestCase):

    def setUp(self):
        super().setUp()

        self.a = KRatioAnalysis()

        self.options = self.create_basic_options()

    def testapply(self):
        list_options = self.a.apply(self.options)
        self.assertEqual(1, len(list_options))

        options = list_options[0]
        self.assertAlmostEqual(self.options.beam.energy_eV, options.beam.energy_eV, 4)
        self.assertAlmostEqual(self.options.beam.particle, options.beam.particle, 4)
        self.assertIsInstance(options.sample, SubstrateSample)
        self.assertEqual(Material.pure(29), options.sample.material)
        self.assertSequenceEqual(self.options.detectors, options.detectors)
        self.assertSequenceEqual(self.options.limits, options.limits)
        self.assertSequenceEqual(self.options.models, options.models)
        self.assertEqual(1, len(options.analyses))
        self.assertIsInstance(options.analyses[0], PhotonIntensityAnalysis)

    def testapply2(self):
        self.options.sample.material = Material.from_formula('Al2O3')
        list_options = self.a.apply(self.options)
        self.assertEqual(2, len(list_options))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
