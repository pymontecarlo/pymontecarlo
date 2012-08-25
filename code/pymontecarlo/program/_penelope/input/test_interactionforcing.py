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

from pymontecarlo.program._penelope.input.interactionforcing import \
    Collisions, InteractionForcing

# Globals and constants variables.
from pymontecarlo.program._penelope.input.interactionforcing import \
    ELECTRON, PHOTON, POSITRON


class TestInteractionForcing(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.coll_el = Collisions(ELECTRON)
        self.if1 = InteractionForcing(ELECTRON, self.coll_el.HARD_BREMSSTRAHLUNG_EMISSION, -4, (0.1, 1.0))
        self.if2 = InteractionForcing(ELECTRON, self.coll_el.INNERSHELL_IMPACT_IONISATION, -400, (0.1, 1.0))

        self.coll_ph = Collisions(PHOTON)
        self.if3 = InteractionForcing(PHOTON, self.coll_ph.INCOHERENT_COMPTON_SCATTERING, -10, (1e-4, 1.0))
        self.if4 = InteractionForcing(PHOTON, self.coll_ph.INCOHERENT_COMPTON_SCATTERING, -10, (1e-4, 1.0))

        self.coll_po = Collisions(POSITRON)
        self.if5 = InteractionForcing(POSITRON, self.coll_po.ANNIHILATION, -100, (1e-4, 1.0))
        self.if6 = InteractionForcing(POSITRON, self.coll_po.DELTA_INTERACTION, -100, (1e-4, 1.0))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(ELECTRON, self.if1.particle)
        self.assertEqual(ELECTRON, self.if2.particle)
        self.assertEqual(PHOTON, self.if3.particle)
        self.assertEqual(PHOTON, self.if4.particle)
        self.assertEqual(POSITRON, self.if5.particle)
        self.assertEqual(POSITRON, self.if6.particle)

        self.assertEqual(self.coll_el.HARD_BREMSSTRAHLUNG_EMISSION, self.if1.collision)
        self.assertEqual(self.coll_el.INNERSHELL_IMPACT_IONISATION, self.if2.collision)
        self.assertEqual(self.coll_ph.INCOHERENT_COMPTON_SCATTERING, self.if3.collision)
        self.assertEqual(self.coll_ph.INCOHERENT_COMPTON_SCATTERING, self.if4.collision)
        self.assertEqual(self.coll_po.ANNIHILATION, self.if5.collision)
        self.assertEqual(self.coll_po.DELTA_INTERACTION, self.if6.collision)

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
        if0 = InteractionForcing(ELECTRON, self.coll_el.HARD_BREMSSTRAHLUNG_EMISSION, -4, (0.1, 1.0))
        self.assertTrue(if0 == self.if1)

    def test__ne__(self):
        if0 = InteractionForcing(PHOTON, self.coll_el.HARD_BREMSSTRAHLUNG_EMISSION, -400, (0.1, 1.0))
        self.assertTrue(if0 != self.if1)

    def test__cmd__(self):
        #From setUp()
        self.assertEqual(cmp(self.if1, self.if2), -1) #interactionForcing1 is less than interactionForcing2

        self.assertEqual(cmp(self.if2, self.if3), -1) #interactionForcing1 is less than interactionForcing3
        self.assertEqual(cmp(self.if1, self.if3), -1) #interactionForcing1 is less than interactionForcing3

        self.assertEqual(cmp(self.if3, self.if4), 0) #interactionForcing3 is less than interactionForcing4
        self.assertEqual(cmp(self.if4, self.if5), -1) #interactionForcing1 is less than interactionForcing2
        self.assertEqual(cmp(self.if5, self.if6), -1) #interactionForcing1 is less than interactionForcing2

        #Other examples
        if1 = InteractionForcing(1, 1, -2)
        if2 = InteractionForcing(2, 1, -2)
        if3 = InteractionForcing(1, 2, -2)
        if4 = InteractionForcing(1, 1, -2)
        if5 = InteractionForcing(2, 2, -2)
        if6 = InteractionForcing(1, 1, -4)
        if7 = InteractionForcing(2, 1, -4)

        self.assertEqual(cmp(if1, if2), -1) #if1 is less than if2
        self.assertEqual(cmp(if1, if3), -1) #if1 is less than if3
        self.assertEqual(cmp(if1, if4), 0) #if1 is equal than if4
        self.assertEqual(cmp(if1, if5), -1) #if1 is less than if5
        self.assertEqual(cmp(if1, if6), 0) #if1 is equal to if6
        self.assertEqual(cmp(if1, if7), -1) #if1 is less than if7

        self.assertEqual(cmp(if2, if3), 1) #if2 is greater than if3
        self.assertEqual(cmp(if2, if4), 1) #if2 is greater than if4
        self.assertEqual(cmp(if2, if5), -1) #if2 is less than if5
        self.assertEqual(cmp(if2, if6), 1) #if2 is greater than if6
        self.assertEqual(cmp(if2, if7), 0) #if2 is equal to if7

        self.assertEqual(cmp(if3, if4), 1) #if3 is greater than if4
        self.assertEqual(cmp(if3, if5), -1) #if3 is less than if5
        self.assertEqual(cmp(if3, if6), 1) #if3 is greater than if6
        self.assertEqual(cmp(if3, if7), -1) #if3 is less than if7

        self.assertEqual(cmp(if4, if5), -1) #if4 is less than if5
        self.assertEqual(cmp(if4, if6), 0) #if4 is equal than if6
        self.assertEqual(cmp(if4, if7), -1) #if4 is less than if7

        self.assertEqual(cmp(if5, if6), 1) #if5 is greater than if6
        self.assertEqual(cmp(if5, if7), 1) #if5 is greater than if7

        self.assertEqual(cmp(if6, if7), -1) #if6 is less than if7

    def testfrom_xml(self):
        element = self.if1.to_xml()
        if1 = InteractionForcing.from_xml(element)

        self.assertEqual(ELECTRON, if1.particle)
        self.assertEqual(self.coll_el.HARD_BREMSSTRAHLUNG_EMISSION, if1.collision)
        self.assertAlmostEqual(-4, if1.forcer, 6)
        self.assertAlmostEqual(0.1, if1.weight[0], 6)
        self.assertAlmostEqual(1.0, if1.weight[1], 6)

    def testto_xml(self):
        element = self.if1.to_xml()

        self.assertEqual(ELECTRON, int(element.get('particle')))
        self.assertEqual(self.coll_el.HARD_BREMSSTRAHLUNG_EMISSION,
                         int(element.get('collision')))
        self.assertAlmostEqual(-4.0, float(element.get('forcer')))
        self.assertAlmostEqual(0.1, float(element.get('weightMin')))
        self.assertAlmostEqual(1.0, float(element.get('weightMax')))

class TestCollisions(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.coll_el = Collisions(ELECTRON)
        self.coll_ph = Collisions(PHOTON)
        self.coll_po = Collisions(POSITRON)

    def tearDown(self):
        TestCase.tearDown(self)

    def testSkeleton(self):
        # Electron
        self.assertEqual(self.coll_el.ARTIFICIAL_SOFT_EVENT, 1)
        self.assertEqual(self.coll_el.HARD_ELASTIC_COLLISION, 2)
        self.assertEqual(self.coll_el.HARD_INELASTIC_COLLISION, 3)
        self.assertEqual(self.coll_el.HARD_BREMSSTRAHLUNG_EMISSION, 4)
        self.assertEqual(self.coll_el.INNERSHELL_IMPACT_IONISATION, 5)
        self.assertEqual(self.coll_el.DELTA_INTERACTION, 7)
        self.assertEqual(self.coll_el.AUXILIARY_INTERACTION, 8)

        # Photon
        self.assertEqual(self.coll_ph.COHERENT_RAYLEIGH_SCATTERING, 1)
        self.assertEqual(self.coll_ph.INCOHERENT_COMPTON_SCATTERING, 2)
        self.assertEqual(self.coll_ph.PHOTOELECTRIC_ABSORPTION, 3)
        self.assertEqual(self.coll_ph.ELECTRON_POSITRON_PAIR_PRODUCTION, 4)
        self.assertEqual(self.coll_ph.DELTA_INTERACTION, 7)
        self.assertEqual(self.coll_ph.AUXILIARY_INTERACTION, 8)

        # Positron
        self.assertEqual(self.coll_po.ARTIFICIAL_SOFT_EVENT, 1)
        self.assertEqual(self.coll_po.HARD_ELASTIC_COLLISION, 2)
        self.assertEqual(self.coll_po.HARD_INELASTIC_COLLISION, 3)
        self.assertEqual(self.coll_po.HARD_BREMSSTRAHLUNG_EMISSION, 4)
        self.assertEqual(self.coll_po.INNERSHELL_IMPACT_IONISATION, 5)
        self.assertEqual(self.coll_po.INNERSHELL_IMPACT_IONISATION, 5)
        self.assertEqual(self.coll_po.ANNIHILATION, 6)
        self.assertEqual(self.coll_po.DELTA_INTERACTION, 7)
        self.assertEqual(self.coll_po.AUXILIARY_INTERACTION, 8)

    def testpossible_collisions(self):
        self.assertEqual(len(self.coll_el.possible_collisions), 7)
        self.assertEqual(len(self.coll_ph.possible_collisions), 6)
        self.assertEqual(len(self.coll_po.possible_collisions), 8)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
