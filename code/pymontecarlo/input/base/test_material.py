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
from pymontecarlo.input.base.material import \
    Material, composition_from_formula, pure, VACUUM

# Globals and constants variables.

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testcomposition_from_formula(self):
        weightFractionAl = 0.21358626371988801
        weightFractionNa = 0.27298103136883051
        weightFractionB = 0.51343270491128157

        comp = composition_from_formula('Al2Na3B12')
        self.assertAlmostEqual(weightFractionAl, comp[13], 4)
        self.assertAlmostEqual(weightFractionNa, comp[11], 4)
        self.assertAlmostEqual(weightFractionB, comp[5], 4)

        comp = composition_from_formula('Al 2 Na 3 B 12')
        self.assertAlmostEqual(weightFractionAl, comp[13], 4)
        self.assertAlmostEqual(weightFractionNa, comp[11], 4)
        self.assertAlmostEqual(weightFractionB, comp[5], 4)

        comp = composition_from_formula('Al2 Na3 B12')
        self.assertAlmostEqual(weightFractionAl, comp[13], 4)
        self.assertAlmostEqual(weightFractionNa, comp[11], 4)
        self.assertAlmostEqual(weightFractionB, comp[5], 4)

        self.assertRaises(ValueError, composition_from_formula, 'Aq2 Na3 B12')

        comp = composition_from_formula('Al2')
        self.assertAlmostEqual(1.0, comp[13], 4)

    def testpure(self):
        m = pure(29)

        self.assertEquals('Copper', str(m))

        self.assertTrue(m.composition.has_key(29))
        self.assertAlmostEqual(1.0, m.composition[29], 4)

        self.assertAlmostEqual(8.96, m.density_kg_m3, 4)

        self.assertAlmostEqual(50, m.absorption_energy_electron_eV, 4)
        self.assertAlmostEqual(50, m.absorption_energy_photon_eV, 4)

    def testVACUUM(self):
        self.assertTrue(VACUUM.is_vacuum())

        self.assertEquals('Vacuum', str(VACUUM))

        self.assertEqual({}, VACUUM.composition)
        self.assertAlmostEqual(0.0, VACUUM.density_kg_m3, 4)

        self.assertAlmostEqual(0.0, VACUUM.absorption_energy_electron_eV, 4)
        self.assertAlmostEqual(0.0, VACUUM.absorption_energy_photon_eV, 4)

class TestMaterial(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.m = Material('Pure Cu', {'Cu': '?'}, density_kg_m3=None)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

        self.assertEquals('Pure Cu', str(self.m))
        self.assertEquals('Pure Cu', self.m.name)

        self.assertTrue(self.m.composition.has_key(29))
        self.assertAlmostEqual(1.0, self.m.composition[29], 4)

        self.assertAlmostEqual(8.96, self.m.density_kg_m3, 4)

        self.assertAlmostEqual(50, self.m.absorption_energy_electron_eV, 4)
        self.assertAlmostEqual(50, self.m.absorption_energy_photon_eV, 4)

    def testfrom_xml(self):
        element = self.m.to_xml()
        m = Material.from_xml(element)

        self.assertEquals('Pure Cu', str(m))

        self.assertTrue(m.composition.has_key(29))
        self.assertAlmostEqual(1.0, m.composition[29], 4)

        self.assertAlmostEqual(8.96, m.density_kg_m3, 4)

        self.assertAlmostEqual(50, m.absorption_energy_electron_eV, 4)
        self.assertAlmostEqual(50, m.absorption_energy_photon_eV, 4)

    def testcomposition(self):
        # Vacuum
        self.m.composition = {}
        self.assertEqual({}, self.m.composition)

        # Wildcard
        self.m.composition = {29: 0.7, 30: '?'}
        self.assertTrue(self.m.composition.has_key(29))
        self.assertAlmostEqual(0.7, self.m.composition[29], 4)
        self.assertTrue(self.m.composition.has_key(30))
        self.assertAlmostEqual(0.3, self.m.composition[30], 4)

        # Multiple wildcards
        self.m.composition = {29: '?', 30: '?'}
        self.assertTrue(self.m.composition.has_key(29))
        self.assertAlmostEqual(0.5, self.m.composition[29], 4)
        self.assertTrue(self.m.composition.has_key(30))
        self.assertAlmostEqual(0.5, self.m.composition[30], 4)

        # ValueError: Incorrect symbol
        self.assertRaises(ValueError, self.m.__setattr__, 'composition', {'Aa': 1.0})

        # ValueError: Incorrect atomic number
        self.assertRaises(ValueError, self.m.__setattr__, 'composition', {-1: 1.0})

        # ValueError: Incorrect fraction
        self.assertRaises(ValueError, self.m.__setattr__, 'composition', {'Cu': 10.0})

        # ValueError: Incorrect total fraction
        self.assertRaises(ValueError, self.m.__setattr__, 'composition', {29: 0.7, 30: 0.7})

    def testdensity_kg_m3(self):
        # Negative density
        self.m.density_kg_m3 = -1
        self.assertAlmostEqual(8.96, self.m.density_kg_m3, 4)

        # User defined density
        self.m.density_kg_m3 = 1.0
        self.assertAlmostEqual(1.0, self.m.density_kg_m3, 4)

    def testabsoprtion_energy_electron_eV(self):
        self.m.absorption_energy_electron_eV = 1e3
        self.assertAlmostEqual(1e3, self.m.absorption_energy_electron_eV, 4)

        # ValueError: Energy less than 0
        self.assertRaises(ValueError, self.m.__setattr__, 'absorption_energy_electron_eV', -1.0)

    def testabsoprtion_energy_photon_eV(self):
        self.m.absorption_energy_photon_eV = 1e3
        self.assertAlmostEqual(1e3, self.m.absorption_energy_photon_eV, 4)

        # ValueError: Energy less than 0
        self.assertRaises(ValueError, self.m.__setattr__, 'absorption_energy_photon_eV', -1.0)

    def testto_xml(self):
        element = self.m.to_xml()

        self.assertEquals('Pure Cu', element.get('name'))

        children = list(element.find('composition'))
        self.assertEqual(1, len(children))
        self.assertEqual(29, int(children[0].get('z')))
        self.assertAlmostEqual(1.0, float(children[0].get('weightFraction')), 4)

        self.assertAlmostEqual(8.96, float(element.get('density')), 4)

        self.assertAlmostEqual(50, float(element.get('absorptionEnergyElectron')), 4)
        self.assertAlmostEqual(50, float(element.get('absorptionEnergyPhoton')), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
