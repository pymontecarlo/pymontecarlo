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

from pymontecarlo.input.particle import ELECTRON, PHOTON, POSITRON
from pymontecarlo.input.collision import \
    (HARD_BREMSSTRAHLUNG_EMISSION, INNERSHELL_IMPACT_IONISATION,
     INCOHERENT_COMPTON_SCATTERING, ANNIHILATION, DELTA)
from pymontecarlo.program._penelope.input.interactionforcing import InteractionForcing

# Globals and constants variables.

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

#    def test__cmd__(self):
#        #From setUp()
#        self.assertEqual(cmp(self.if1, self.if2), -1) #interactionForcing1 is less than interactionForcing2
#
#        self.assertEqual(cmp(self.if2, self.if3), -1) #interactionForcing1 is less than interactionForcing3
#        self.assertEqual(cmp(self.if1, self.if3), -1) #interactionForcing1 is less than interactionForcing3
#
#        self.assertEqual(cmp(self.if3, self.if4), 0) #interactionForcing3 is less than interactionForcing4
#        self.assertEqual(cmp(self.if4, self.if5), -1) #interactionForcing1 is less than interactionForcing2
#        self.assertEqual(cmp(self.if5, self.if6), -1) #interactionForcing1 is less than interactionForcing2
#
#        #Other examples
#        if1 = InteractionForcing(1, 1, -2)
#        if2 = InteractionForcing(2, 1, -2)
#        if3 = InteractionForcing(1, 2, -2)
#        if4 = InteractionForcing(1, 1, -2)
#        if5 = InteractionForcing(2, 2, -2)
#        if6 = InteractionForcing(1, 1, -4)
#        if7 = InteractionForcing(2, 1, -4)
#
#        self.assertEqual(cmp(if1, if2), -1) #if1 is less than if2
#        self.assertEqual(cmp(if1, if3), -1) #if1 is less than if3
#        self.assertEqual(cmp(if1, if4), 0) #if1 is equal than if4
#        self.assertEqual(cmp(if1, if5), -1) #if1 is less than if5
#        self.assertEqual(cmp(if1, if6), 0) #if1 is equal to if6
#        self.assertEqual(cmp(if1, if7), -1) #if1 is less than if7
#
#        self.assertEqual(cmp(if2, if3), 1) #if2 is greater than if3
#        self.assertEqual(cmp(if2, if4), 1) #if2 is greater than if4
#        self.assertEqual(cmp(if2, if5), -1) #if2 is less than if5
#        self.assertEqual(cmp(if2, if6), 1) #if2 is greater than if6
#        self.assertEqual(cmp(if2, if7), 0) #if2 is equal to if7
#
#        self.assertEqual(cmp(if3, if4), 1) #if3 is greater than if4
#        self.assertEqual(cmp(if3, if5), -1) #if3 is less than if5
#        self.assertEqual(cmp(if3, if6), 1) #if3 is greater than if6
#        self.assertEqual(cmp(if3, if7), -1) #if3 is less than if7
#
#        self.assertEqual(cmp(if4, if5), -1) #if4 is less than if5
#        self.assertEqual(cmp(if4, if6), 0) #if4 is equal than if6
#        self.assertEqual(cmp(if4, if7), -1) #if4 is less than if7
#
#        self.assertEqual(cmp(if5, if6), 1) #if5 is greater than if6
#        self.assertEqual(cmp(if5, if7), 1) #if5 is greater than if7
#
#        self.assertEqual(cmp(if6, if7), -1) #if6 is less than if7

    def testfrom_xml(self):
        element = self.if1.to_xml()
        if1 = InteractionForcing.from_xml(element)

        self.assertIs(ELECTRON, if1.particle)
        self.assertIs(HARD_BREMSSTRAHLUNG_EMISSION, if1.collision)
        self.assertAlmostEqual(-4, if1.forcer, 6)
        self.assertAlmostEqual(0.1, if1.weight[0], 6)
        self.assertAlmostEqual(1.0, if1.weight[1], 6)

    def testto_xml(self):
        element = self.if1.to_xml()

        self.assertEqual('electron', element.get('particle'))
        self.assertEqual('hard bremsstrahlung emission',
                         element.get('collision'))
        self.assertAlmostEqual(-4.0, float(element.get('forcer')))
        self.assertAlmostEqual(0.1, float(element.get('weightMin')))
        self.assertAlmostEqual(1.0, float(element.get('weightMax')))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
