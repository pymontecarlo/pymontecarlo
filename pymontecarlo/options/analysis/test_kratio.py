#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.analysis.kratio import KRatioAnalysis
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.material import Material
from pymontecarlo.options.options import Options
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.simulation import Simulation
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResultBuilder
from pymontecarlo.results.kratio import KRatioResult

# Globals and constants variables.

class TestKRatioAnalysis(TestCase):

    def setUp(self):
        super().setUp()

        photon_detector = self.create_basic_photondetector()
        self.a = KRatioAnalysis(photon_detector)

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

#    def testcalculate_nothing(self):
#        simulation = self.create_basic_simulation()
#        simulations = [simulation]
#        newresult = self.a.calculate(simulation, simulations)
#        self.assertFalse(newresult)

    def testcalculate(self):
        # Create options
        beam = GaussianBeam(20e3, 10.e-9)
        sample = SubstrateSample(Material.from_formula('CaSiO4'))
        limit = ShowersLimit(100)
        unkoptions = Options(self.program, beam, sample, [self.a], [limit])

        list_standard_options = self.a.apply(unkoptions)
        self.assertEqual(3, len(list_standard_options))

        # Create simulations
        def create_simulation(options):
            builder = EmittedPhotonIntensityResultBuilder(self.a)
            for z, wf in options.sample.material.composition.items():
                builder.add_intensity((z, 'Ka'), wf * 1e3, math.sqrt(wf * 1e3))
            result = builder.build()
            return Simulation(options, [result])

        unksim = create_simulation(unkoptions)
        stdsims = [create_simulation(options) for options in list_standard_options]
        sims = stdsims + [unksim]

        # Calculate
        newresult = self.a.calculate(unksim, sims)
        self.assertTrue(newresult)

        newresult = self.a.calculate(unksim, sims)
        self.assertFalse(newresult)

        # Test
        results = unksim.find_result(KRatioResult)
        self.assertEqual(1, len(results))

        result = results[0]
        self.assertEqual(3, len(result))

        q = result[('Ca', 'Ka')]
        self.assertAlmostEqual(0.303262, q.n, 4)
        self.assertAlmostEqual(0.019880, q.s, 4)

        q = result[('Si', 'Ka')]
        self.assertAlmostEqual(0.212506, q.n, 4)
        self.assertAlmostEqual(0.016052, q.s, 4)

        q = result[('O', 'Ka')]
        self.assertAlmostEqual(0.484232 / 0.470749, q.n, 4)
        self.assertAlmostEqual(0.066579, q.s, 4)

if __name__ == '__main__': #pragma: no cover
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
