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
import copy
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.particle import ELECTRON, PHOTON, POSITRON
from pymontecarlo.options.material import \
    Material, composition_from_formula, pure, _Composition, _AbsorptionEnergy, VACUUM
from pymontecarlo.options.xmlmapper import mapper

# Globals and constants variables.

warnings.simplefilter("always")

class TestModule(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

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

        self.assertEqual('Copper', str(m))

        self.assertTrue(29 in m.composition)
        self.assertAlmostEqual(1.0, m.composition[29], 4)

        self.assertAlmostEqual(8.96, m.density_kg_m3 / 1000.0, 4)
        self.assertAlmostEqual(8.96, m.density_g_cm3, 4)

        self.assertAlmostEqual(50, m.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(50, m.absorption_energy_eV[PHOTON], 4)

class TestVACUUM(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Vacuum', str(VACUUM))
        self.assertEqual({}, VACUUM.composition)
        self.assertAlmostEqual(0.0, VACUUM.density_kg_m3, 4)
        self.assertAlmostEqual(0.0, VACUUM.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(0.0, VACUUM.absorption_energy_eV[PHOTON], 4)
        self.assertAlmostEqual(0.0, VACUUM.absorption_energy_eV[POSITRON], 4)

        self.assertRaises(AttributeError, setattr, VACUUM, 'name', 'test')

    def testcopy(self):
        self.assertIs(VACUUM, copy.copy(VACUUM))
        self.assertIs(VACUUM, copy.deepcopy(VACUUM))

    def testfrom_xml(self):
        element = mapper.to_xml(VACUUM)
        obj = mapper.from_xml(element)

        self.assertIs(obj, VACUUM)
#
    def testto_xml(self):
        element = mapper.to_xml(VACUUM)

        self.assertEqual(0, len(list(element)))

class Test_Composition(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.comp = _Composition()
        self.comp.update({29: 0.4, 'Zn': [0.5, '?'], 'Ni': ['?']})

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(29 in self.comp)
        self.assertAlmostEqual(0.4, self.comp[29])

        self.assertTrue(30 in self.comp)
        self.assertEqual(2, len(self.comp[30]))

    def testcalculate(self):
        self.comp.calculate()

        self.assertEqual(2, len(self.comp[29]))
        self.assertAlmostEqual(0.4, self.comp[29][0], 4)
        self.assertAlmostEqual(0.4, self.comp[29][1], 4)

        self.assertEqual(2, len(self.comp[30]))
        self.assertAlmostEqual(0.5, self.comp[30][0], 4)
        self.assertAlmostEqual(0.3, self.comp[30][1], 4)

        self.assertEqual(2, len(self.comp[28]))
        self.assertAlmostEqual(0.1, self.comp[28][0], 4)
        self.assertAlmostEqual(0.3, self.comp[28][1], 4)

class Test_AbsorptionEnergy(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.ae = _AbsorptionEnergy(56.8)

    def tearDown(self):
        TestCase.tearDown(self)

    def testdefault(self):
        self.assertAlmostEqual(56.8, self.ae[ELECTRON], 4)
        self.assertAlmostEqual(56.8, self.ae[PHOTON], 4)
        self.assertAlmostEqual(56.8, self.ae[POSITRON], 4)

    def test__setitem__(self):
        self.ae[ELECTRON] = 1e3
        self.assertAlmostEqual(1e3, self.ae[ELECTRON], 4)

        # ValueError: Energy less than 0
        self.assertRaises(ValueError, self.ae.__setitem__, ELECTRON, -1.0)

        # Only particle key are accepted
        self.assertRaises(KeyError, self.ae.__setitem__, "blah", 50.0)

class TestMaterial(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.m = Material('Pure Cu', {'Cu': '?'}, density_kg_m3=None)
        self.m.absorption_energy_eV[ELECTRON] = 50.0
        self.m.absorption_energy_eV[PHOTON] = 51.0
        self.m.absorption_energy_eV[POSITRON] = 52.0

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

        self.assertEqual('Pure Cu', str(self.m))
        self.assertEqual('Pure Cu', self.m.name)

        self.assertTrue(29 in self.m.composition)
        self.assertEqual('?', self.m.composition[29])

        self.assertIsNone(self.m.density_kg_m3)

        self.assertAlmostEqual(50, self.m.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(51, self.m.absorption_energy_eV[PHOTON], 4)
        self.assertAlmostEqual(52, self.m.absorption_energy_eV[POSITRON], 4)

    def testcomposition(self):
        self.m.composition[29] = [0.5, 0.6]

        # ValueError: Incorrect symbol
        self.assertRaises(ValueError, self.m.composition.update, {'Aa': 1.0})

        # ValueError: Incorrect atomic number
        self.assertRaises(ValueError, self.m.composition.update, {-1: 1.0})

        # ValueError: Incorrect fraction
        self.assertRaises(ValueError, self.m.composition.update, {'Cu': 10.0})

        # ValueError: Incorrect total fraction
        self.m.composition.update({29: 0.7, 30: 0.7})
        self.assertRaises(ValueError, self.m.composition.calculate)

#    def testcomposition_atomic(self):
#        # Wildcard
#        self.m.composition = {29: 0.7, 30: '?'}
#        self.assertTrue(self.m.composition_atomic.has_key(29))
#        self.assertAlmostEqual(0.70594, self.m.composition_atomic[29], 4)
#        self.assertTrue(self.m.composition_atomic.has_key(30))
#        self.assertAlmostEqual(0.29405, self.m.composition_atomic[30], 4)
#
#        # Multiple wildcards
#        self.m.composition = {29: '?', 30: '?'}
#        self.assertTrue(self.m.composition_atomic.has_key(29))
#        self.assertAlmostEqual(0.50711, self.m.composition_atomic[29], 4)
#        self.assertTrue(self.m.composition_atomic.has_key(30))
#        self.assertAlmostEqual(0.49289, self.m.composition_atomic[30], 4)

    def testdensity_kg_m3(self):
        # Negative density
        self.m.density_kg_m3 = None
        self.assertIsNone(self.m.density_kg_m3)
        self.assertIsNone(self.m.density_g_cm3)

        # User defined density
        self.m.density_kg_m3 = 1.0
        self.assertAlmostEqual(1.0, self.m.density_kg_m3, 4)

    def testcalculate(self):
        self.m.calculate()

        self.assertAlmostEqual(1.0, self.m.composition[29], 4)
        self.assertAlmostEqual(8960, self.m.density_kg_m3, 4)

        # Wildcard
        self.m.composition.update({29: 0.7, 30: '?'})
        self.m.density_kg_m3 = None
        self.m.calculate()

        self.assertAlmostEqual(8323.4973, self.m.density_kg_m3, 4)
        self.assertTrue(29 in self.m.composition)
        self.assertAlmostEqual(0.7, self.m.composition[29], 4)
        self.assertTrue(30 in self.m.composition)
        self.assertAlmostEqual(0.3, self.m.composition[30], 4)

        # Multiple wildcards
        self.m.composition.update({29: '?', 30: '?'})
        self.m.density_kg_m3 = None
        self.m.calculate()

        self.assertAlmostEqual(7947.1304, self.m.density_kg_m3, 4)
        self.assertTrue(29 in self.m.composition)
        self.assertAlmostEqual(0.5, self.m.composition[29], 4)
        self.assertTrue(30 in self.m.composition)
        self.assertAlmostEqual(0.5, self.m.composition[30], 4)

        # Multiple values
        self.m.composition.update({29: 0.4, 'Zn': [0.5, '?'], 'Ni': ['?']})
        self.m.density_kg_m3 = None

        with warnings.catch_warnings(record=True) as ws:
            self.m.calculate()

        self.assertEqual(1, len(ws))
        self.assertIsNone(self.m.density_kg_m3)
        self.assertEqual(2, len(self.m.composition[29]))
        self.assertAlmostEqual(0.4, self.m.composition[29][0], 4)
        self.assertAlmostEqual(0.4, self.m.composition[29][1], 4)

        self.assertEqual(2, len(self.m.composition[30]))
        self.assertAlmostEqual(0.5, self.m.composition[30][0], 4)
        self.assertAlmostEqual(0.3, self.m.composition[30][1], 4)

        self.assertEqual(2, len(self.m.composition[28]))
        self.assertAlmostEqual(0.1, self.m.composition[28][0], 4)
        self.assertAlmostEqual(0.3, self.m.composition[28][1], 4)

    def testfrom_xml(self):
        element = mapper.to_xml(self.m)
        m = mapper.from_xml(element)

        self.assertEqual('Pure Cu', str(m))

        self.assertIn(29, m.composition)
        self.assertEqual('?', m.composition[29], 4)

        self.assertIsNone(m.density_kg_m3)

        self.assertAlmostEqual(50, m.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(51, m.absorption_energy_eV[PHOTON], 4)
        self.assertAlmostEqual(52, m.absorption_energy_eV[POSITRON], 4)

        self.assertFalse(hasattr(m, '_index'))

    def testto_xml(self):
        element = mapper.to_xml(self.m)

        self.assertEqual('Pure Cu', element.get('name'))

        children = list(element.find('composition'))
        self.assertEqual(1, len(children))
        self.assertEqual(29, int(children[0].get('z')))
        self.assertEqual('?', children[0].text)

        self.assertEqual('xsi:nil', element.get('density'))

        children = list(element.find('absorption_energy'))
        self.assertEqual(3, len(children))

        values = dict([(child.get('particle'), float(child.text)) for child in children])
        self.assertIn("electron", values)
        self.assertAlmostEqual(50, values["electron"], 4)
        self.assertIn("photon", values)
        self.assertAlmostEqual(51, values["photon"], 4)
        self.assertIn("positron", values)
        self.assertAlmostEqual(52, values["positron"], 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
