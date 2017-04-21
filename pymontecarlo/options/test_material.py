#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import copy
import pickle

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.material import Material, VACUUM, MaterialBuilder

# Globals and constants variables.

class TestVACUUM(TestCase):

    def testskeleton(self):
        self.assertEqual('Vacuum', str(VACUUM))
        self.assertEqual({}, VACUUM.composition)
        self.assertAlmostEqual(0.0, VACUUM.density_kg_per_m3, 4)
        self.assertTupleEqual((0.0, 0.0, 0.0, 0.0), VACUUM.color)

    def testcopy(self):
        self.assertIs(VACUUM, copy.copy(VACUUM))
        self.assertIs(VACUUM, copy.deepcopy(VACUUM))

    def testpickle(self):
        self.assertIs(VACUUM, pickle.loads(pickle.dumps(VACUUM)))

    def test__repr__(self):
        expected = '<Vacuum()>'
        self.assertEqual(expected, repr(VACUUM))

class TestMaterial(TestCase):

    def setUp(self):
        super().setUp()

        self.m = Material('Pure Cu', {29: 1.0}, 8960.0, '#FF0000')

    def testskeleton(self):
        self.assertTrue(True)

        self.assertEqual('Pure Cu', str(self.m))
        self.assertEqual('Pure Cu', self.m.name)

        self.assertTrue(29 in self.m.composition)
        self.assertAlmostEqual(1.0, self.m.composition[29])

        self.assertAlmostEqual(8960.0, self.m.density_kg_per_m3, 4)
        self.assertAlmostEqual(8.960, self.m.density_g_per_cm3, 4)

        self.assertEqual('#FF0000', self.m.color)

    def testpure(self):
        m = Material.pure(29)

        self.assertEqual('Copper', str(m))

        self.assertIn(29, m.composition)
        self.assertAlmostEqual(1.0, m.composition[29], 4)

        self.assertAlmostEqual(8.96, m.density_kg_per_m3 / 1000.0, 4)
        self.assertAlmostEqual(8.96, m.density_g_per_cm3, 4)

    def testfrom_formula(self):
        m = Material.from_formula('SiO2', 1250.0)

        self.assertEqual('SiO2', str(m))

        self.assertIn(14, m.composition)
        self.assertAlmostEqual(0.4674, m.composition[14], 4)

        self.assertIn(8, m.composition)
        self.assertAlmostEqual(0.5326, m.composition[8], 4)

        self.assertAlmostEqual(1.25, m.density_kg_per_m3 / 1000.0, 4)
        self.assertAlmostEqual(1.25, m.density_g_per_cm3, 4)

    def test__repr__(self):
        expected = '<Material(Pure Cu, 100%Cu, 8960 kg/m3)>'
        self.assertEqual(expected, repr(self.m))

    def test__eq__(self):
        m2 = Material('Pure Cu', {29: 1.0}, 8960.0)
        self.assertEqual(m2, self.m)

        m2 = Material('Pure Cu', {29: 1.0}, 8961.0)
        self.assertNotEqual(m2, self.m)

        m2 = Material('Pure Cu', {29: 0.5, 30: 0.5}, 8960.0)
        self.assertNotEqual(m2, self.m)

    def testset_color_set(self):
        Material.set_color_set(['#00FF00', '#0000FF'])

        m = Material.pure(13)
        self.assertEqual('#00FF00', m.color)

        m = Material.pure(14)
        self.assertEqual('#0000FF', m.color)

        m = Material.pure(15)
        self.assertEqual('#00FF00', m.color)

class TestMaterialBuilder(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.b = MaterialBuilder(26)
        self.b.add_element(29, 0.05)
        self.b.add_element_range(28, 0.1, 0.2, 0.02)
        self.b.add_element(24, (0.01, 0.05, 0.07))
        self.b.add_element_interval(6, 0.0, 1.0, 5)

    def tearDown(self):
        TestCase.tearDown(self)

    def test__len__(self):
        self.assertEqual(5 * 3 * 5, len(self.b))

    def testbuild(self):
        compositions = self.b.build()
        self.assertEqual(5 * 3 * 5, len(compositions))

    def testno_element(self):
        b = MaterialBuilder(26)
        self.assertEqual(1, len(b))
        self.assertEqual(1, len(b.build()))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
