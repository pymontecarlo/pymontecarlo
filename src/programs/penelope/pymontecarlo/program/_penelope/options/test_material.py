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
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.particle import ELECTRON, PHOTON, POSITRON

from pymontecarlo.program._penelope.options.material import \
    Material, InteractionForcing

# Globals and constants variables.
from pymontecarlo.options.collision import \
    (HARD_BREMSSTRAHLUNG_EMISSION, INNERSHELL_IMPACT_IONISATION,
     INCOHERENT_COMPTON_SCATTERING, ANNIHILATION, DELTA)

class TestInteractionForcing(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.if1 = InteractionForcing(ELECTRON, HARD_BREMSSTRAHLUNG_EMISSION, -4, (0.1, 1.0))
        self.if2 = InteractionForcing(ELECTRON, INNERSHELL_IMPACT_IONISATION, -400, (0.1, 1.0))

        self.if3 = InteractionForcing(PHOTON, INCOHERENT_COMPTON_SCATTERING, -10, (1e-4, 1.0))
        self.if4 = InteractionForcing(PHOTON, INCOHERENT_COMPTON_SCATTERING, -10, (1e-4, 1.0))

        self.if5 = InteractionForcing(POSITRON, ANNIHILATION, -100, (1e-4, 1.0))
        self.if6 = InteractionForcing(POSITRON, DELTA, -100, (1e-4, 1.0))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertIs(ELECTRON, self.if1.particle)
        self.assertIs(ELECTRON, self.if2.particle)
        self.assertIs(PHOTON, self.if3.particle)
        self.assertIs(PHOTON, self.if4.particle)
        self.assertIs(POSITRON, self.if5.particle)
        self.assertIs(POSITRON, self.if6.particle)

        self.assertIs(HARD_BREMSSTRAHLUNG_EMISSION, self.if1.collision)
        self.assertIs(INNERSHELL_IMPACT_IONISATION, self.if2.collision)
        self.assertIs(INCOHERENT_COMPTON_SCATTERING, self.if3.collision)
        self.assertIs(INCOHERENT_COMPTON_SCATTERING, self.if4.collision)
        self.assertIs(ANNIHILATION, self.if5.collision)
        self.assertIs(DELTA, self.if6.collision)

        self.assertAlmostEqual(-4, self.if1.forcer, 6)
        self.assertAlmostEqual(-400, self.if2.forcer, 6)
        self.assertAlmostEqual(-10, self.if3.forcer, 6)
        self.assertAlmostEqual(-10, self.if4.forcer, 6)
        self.assertAlmostEqual(-100, self.if5.forcer, 6)
        self.assertAlmostEqual(-100, self.if5.forcer, 6)

        self.assertAlmostEqual(0.1, self.if1.weight[0], 6)
        self.assertAlmostEqual(0.1, self.if2.weight[0], 6)
        self.assertAlmostEqual(1e-4, self.if3.weight[0], 6)
        self.assertAlmostEqual(1e-4, self.if4.weight[0], 6)
        self.assertAlmostEqual(1e-4, self.if5.weight[0], 6)
        self.assertAlmostEqual(1e-4, self.if6.weight[0], 6)

        self.assertAlmostEqual(1.0, self.if1.weight[1], 6)
        self.assertAlmostEqual(1.0, self.if2.weight[1], 6)
        self.assertAlmostEqual(1.0, self.if3.weight[1], 6)
        self.assertAlmostEqual(1.0, self.if4.weight[1], 6)
        self.assertAlmostEqual(1.0, self.if5.weight[1], 6)
        self.assertAlmostEqual(1.0, self.if6.weight[1], 6)

    def test__eq__(self):
        if0 = InteractionForcing(ELECTRON, HARD_BREMSSTRAHLUNG_EMISSION,
                                 - 4, (0.1, 1.0))
        self.assertTrue(if0 == self.if1)

    def test__ne__(self):
        if0 = InteractionForcing(PHOTON, HARD_BREMSSTRAHLUNG_EMISSION,
                                 - 400, (0.1, 1.0))
        self.assertTrue(if0 != self.if1)

class TestMaterial(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        if1 = InteractionForcing(ELECTRON, HARD_BREMSSTRAHLUNG_EMISSION,
                                 - 4, (0.1, 1.0))
        self.m = Material({'Cu': 1.0}, 'Pure Cu', density_kg_m3=8960.0,
                          elastic_scattering=(0.1, 0.2),
                          cutoff_energy_inelastic_eV=51.2,
                          cutoff_energy_bremsstrahlung_eV=53.4,
                          interaction_forcings=[if1],
                          maximum_step_length_m=123.456)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

        self.assertEqual('Pure Cu', str(self.m))
        self.assertEqual('Pure Cu', self.m.name)

        self.assertTrue(29 in self.m.composition)
        self.assertAlmostEqual(1.0, self.m.composition[29], 4)

        self.assertAlmostEqual(8.96, self.m.density_kg_m3 / 1000.0, 4)

        self.assertAlmostEqual(50, self.m.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(50, self.m.absorption_energy_eV[PHOTON], 4)
        self.assertAlmostEqual(50, self.m.absorption_energy_eV[POSITRON], 4)

        self.assertAlmostEqual(0.1, self.m.elastic_scattering[0], 4)
        self.assertAlmostEqual(0.2, self.m.elastic_scattering[1], 4)

        self.assertAlmostEqual(51.2, self.m.cutoff_energy_inelastic_eV, 4)
        self.assertAlmostEqual(53.4, self.m.cutoff_energy_bremsstrahlung_eV, 4)

        self.assertEqual(1, len(self.m.interaction_forcings))
        if1 = list(self.m.interaction_forcings)[0]
        self.assertIs(ELECTRON, if1.particle)
        self.assertIs(HARD_BREMSSTRAHLUNG_EMISSION, if1.collision)
        self.assertAlmostEqual(-4, if1.forcer, 6)
        self.assertAlmostEqual(0.1, if1.weight[0], 6)
        self.assertAlmostEqual(1.0, if1.weight[1], 6)

        self.assertAlmostEqual(123.456, self.m.maximum_step_length_m, 4)

    def testpure(self):
        m = Material.pure(29)

        self.assertEqual('Copper', str(m))

        self.assertTrue(29 in m.composition)
        self.assertAlmostEqual(1.0, m.composition[29], 4)

        self.assertAlmostEqual(8.96, m.density_kg_m3 / 1000.0, 4)

        self.assertAlmostEqual(50, m.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(50, m.absorption_energy_eV[PHOTON], 4)
        self.assertAlmostEqual(50, m.absorption_energy_eV[POSITRON], 4)

        self.assertAlmostEqual(0.0, m.elastic_scattering[0], 4)
        self.assertAlmostEqual(0.0, m.elastic_scattering[1], 4)

        self.assertAlmostEqual(50.0, m.cutoff_energy_inelastic_eV, 4)
        self.assertAlmostEqual(50.0, m.cutoff_energy_bremsstrahlung_eV, 4)

        self.assertEqual(0, len(m.interaction_forcings))

        self.assertAlmostEqual(1e20, m.maximum_step_length_m, 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

