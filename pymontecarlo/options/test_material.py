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
import pickle

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.particle import ELECTRON, PHOTON, POSITRON
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.

class TestVACUUM(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Vacuum', str(VACUUM))
        self.assertEqual({}, VACUUM.composition)
        self.assertEqual({}, VACUUM.composition_atomic)
        self.assertAlmostEqual(0.0, VACUUM.density_kg_m3, 4)
        self.assertAlmostEqual(0.0, VACUUM.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(0.0, VACUUM.absorption_energy_eV[PHOTON], 4)
        self.assertAlmostEqual(0.0, VACUUM.absorption_energy_eV[POSITRON], 4)

        self.assertRaises(AttributeError, setattr, VACUUM, 'name', 'test')

    def testcopy(self):
        self.assertIs(VACUUM, copy.copy(VACUUM))
        self.assertIs(VACUUM, copy.deepcopy(VACUUM))

    def testpickle(self):
        self.assertIs(VACUUM, pickle.loads(pickle.dumps(VACUUM)))

#     def testfrom_xml(self):
#         element = mapper.to_xml(VACUUM)
#         obj = mapper.from_xml(element)
#
#         self.assertIs(obj, VACUUM)
# #
#     def testto_xml(self):
#         element = mapper.to_xml(VACUUM)
#
#         self.assertEqual(0, len(list(element)))

class TestMaterial(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.m = Material({'Cu': '?'}, 'Pure Cu', None,
                          {ELECTRON: 50.0, PHOTON: 51.0, POSITRON: 52.0})

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

        self.assertEqual('Pure Cu', str(self.m))
        self.assertEqual('Pure Cu', self.m.name)

        self.assertTrue(29 in self.m.composition)
        self.assertAlmostEqual(1.0, self.m.composition[29])

        self.assertAlmostEqual(8960.0, self.m.density_kg_m3, 4)
        self.assertAlmostEqual(8.960, self.m.density_g_cm3, 4)

        self.assertAlmostEqual(50, self.m.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(51, self.m.absorption_energy_eV[PHOTON], 4)
        self.assertAlmostEqual(52, self.m.absorption_energy_eV[POSITRON], 4)

    def testcomposition_from_formula(self):
        weightFractionAl = 0.21358626371988801
        weightFractionNa = 0.27298103136883051
        weightFractionB = 0.51343270491128157

        comp = Material.composition_from_formula('Al2Na3B12')
        self.assertAlmostEqual(weightFractionAl, comp[13], 4)
        self.assertAlmostEqual(weightFractionNa, comp[11], 4)
        self.assertAlmostEqual(weightFractionB, comp[5], 4)

        comp = Material.composition_from_formula('Al 2 Na 3 B 12')
        self.assertAlmostEqual(weightFractionAl, comp[13], 4)
        self.assertAlmostEqual(weightFractionNa, comp[11], 4)
        self.assertAlmostEqual(weightFractionB, comp[5], 4)

        comp = Material.composition_from_formula('Al2 Na3 B12')
        self.assertAlmostEqual(weightFractionAl, comp[13], 4)
        self.assertAlmostEqual(weightFractionNa, comp[11], 4)
        self.assertAlmostEqual(weightFractionB, comp[5], 4)

        self.assertRaises(ValueError, Material.composition_from_formula, 'Aq2 Na3 B12')

        comp = Material.composition_from_formula('Al2')
        self.assertAlmostEqual(1.0, comp[13], 4)

    def testpure(self):
        m = Material.pure(29)

        self.assertEqual('Copper', str(m))

        self.assertIn(29, m.composition)
        self.assertAlmostEqual(1.0, m.composition[29], 4)

        self.assertIn(29, self.m.composition_atomic)
        self.assertAlmostEqual(1.0, self.m.composition_atomic[29], 4)

        self.assertAlmostEqual(8.96, m.density_kg_m3 / 1000.0, 4)
        self.assertAlmostEqual(8.96, m.density_g_cm3, 4)

        self.assertAlmostEqual(50, m.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(50, m.absorption_energy_eV[PHOTON], 4)

    def testcomposition_atomic(self):
        # Wildcard
        m = Material({29: 0.7, 30: '?'})

        self.assertIn(29, m.composition_atomic)
        self.assertAlmostEqual(0.70594, m.composition_atomic[29], 4)
        self.assertIn(30, m.composition_atomic)
        self.assertAlmostEqual(0.29405, m.composition_atomic[30], 4)

        # Multiple wildcards
        m = Material({29: '?', 30: '?'})
        self.assertIn(29, m.composition_atomic)
        self.assertAlmostEqual(0.50711, m.composition_atomic[29], 4)
        self.assertIn(30, m.composition_atomic)
        self.assertAlmostEqual(0.49289, m.composition_atomic[30], 4)

    def testcalculate_composition(self):
        # Wildcard
        composition = Material.calculate_composition({29: 0.7, 30: '?'})

        self.assertIn(29, composition)
        self.assertAlmostEqual(0.7, composition[29], 4)
        self.assertIn(30, composition)
        self.assertAlmostEqual(0.3, composition[30], 4)

        # Multiple wildcards
        composition = Material.calculate_composition({29: '?', 30: '?'})

        self.assertIn(29, composition)
        self.assertAlmostEqual(0.5, composition[29], 4)
        self.assertIn(30, composition)
        self.assertAlmostEqual(0.5, composition[30], 4)

    def testabsorption_energy_eV(self):
        m = Material({'Cu': '?'}, 'Pure Cu', None, 52)
        self.assertAlmostEqual(52, m.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(52, m.absorption_energy_eV[PHOTON], 4)
        self.assertAlmostEqual(52, m.absorption_energy_eV[POSITRON], 4)

        m = Material({'Cu': '?'}, 'Pure Cu', None, {PHOTON: 51.0})
        self.assertAlmostEqual(Material.DEFAULT_ABSORPTION_ENERGY_eV, m.absorption_energy_eV[ELECTRON], 4)
        self.assertAlmostEqual(51, m.absorption_energy_eV[PHOTON], 4)
        self.assertAlmostEqual(Material.DEFAULT_ABSORPTION_ENERGY_eV, m.absorption_energy_eV[POSITRON], 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
