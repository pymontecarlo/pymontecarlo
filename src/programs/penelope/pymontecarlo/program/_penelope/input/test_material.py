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

from pymontecarlo.input.xmlmapper import mapper

from pymontecarlo.program._penelope.input.material import Material, pure

# Globals and constants variables.

class TestModule(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testpure(self):
        m = pure(29)

        self.assertEquals('Copper', str(m))

        self.assertTrue(29 in m.composition)
        self.assertAlmostEqual(1.0, m.composition[29], 4)

        self.assertAlmostEqual(8.96, m.density_kg_m3 / 1000.0, 4)

        self.assertAlmostEqual(50, m.absorption_energy_electron_eV, 4)
        self.assertAlmostEqual(50, m.absorption_energy_photon_eV, 4)
        self.assertAlmostEqual(50, m.absorption_energy_positron_eV, 4)

        self.assertAlmostEqual(0.0, m.elastic_scattering[0], 4)
        self.assertAlmostEqual(0.0, m.elastic_scattering[1], 4)

        self.assertAlmostEqual(50.0, m.cutoff_energy_inelastic_eV, 4)
        self.assertAlmostEqual(50.0, m.cutoff_energy_bremsstrahlung_eV, 4)

class TestMaterial(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.m = Material('Pure Cu', {'Cu': 1.0}, density_kg_m3=8960.0,
                          elastic_scattering=(0.1, 0.2),
                          cutoff_energy_inelastic_eV=51.2,
                          cutoff_energy_bremsstrahlung_eV=53.4)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

        self.assertEquals('Pure Cu', str(self.m))
        self.assertEquals('Pure Cu', self.m.name)

        self.assertTrue(29 in self.m.composition)
        self.assertAlmostEqual(1.0, self.m.composition[29], 4)

        self.assertAlmostEqual(8.96, self.m.density_kg_m3 / 1000.0, 4)

        self.assertAlmostEqual(50, self.m.absorption_energy_electron_eV, 4)
        self.assertAlmostEqual(50, self.m.absorption_energy_photon_eV, 4)
        self.assertAlmostEqual(50, self.m.absorption_energy_positron_eV, 4)

        self.assertAlmostEqual(0.1, self.m.elastic_scattering[0], 4)
        self.assertAlmostEqual(0.2, self.m.elastic_scattering[1], 4)

        self.assertAlmostEqual(51.2, self.m.cutoff_energy_inelastic_eV, 4)
        self.assertAlmostEqual(53.4, self.m.cutoff_energy_bremsstrahlung_eV, 4)

    def testfrom_xml(self):
        element = mapper.to_xml(self.m)
        m = mapper.from_xml(element)

        self.assertEquals('Pure Cu', str(m))

        self.assertTrue(29 in m.composition)
        self.assertAlmostEqual(1.0, m.composition[29], 4)

        self.assertAlmostEqual(8.96, m.density_kg_m3 / 1000.0, 4)

        self.assertAlmostEqual(50, m.absorption_energy_electron_eV, 4)
        self.assertAlmostEqual(50, m.absorption_energy_photon_eV, 4)
        self.assertAlmostEqual(50, m.absorption_energy_positron_eV, 4)

        self.assertAlmostEqual(0.1, m.elastic_scattering[0], 4)
        self.assertAlmostEqual(0.2, m.elastic_scattering[1], 4)

        self.assertAlmostEqual(51.2, m.cutoff_energy_inelastic_eV, 4)
        self.assertAlmostEqual(53.4, m.cutoff_energy_bremsstrahlung_eV, 4)

    def testelastic_scattering(self):
        self.m.elastic_scattering = 0.05, 0.06
        self.assertAlmostEqual(0.05, self.m.elastic_scattering[0], 4)
        self.assertAlmostEqual(0.06, self.m.elastic_scattering[1], 4)

        self.assertRaises(ValueError, self.m.__setattr__, 'elastic_scattering', (-0.1, 0.1))
        self.assertRaises(ValueError, self.m.__setattr__, 'elastic_scattering', (0.1, -0.1))
        self.assertRaises(ValueError, self.m.__setattr__, 'elastic_scattering', (0.3, 0.1))
        self.assertRaises(ValueError, self.m.__setattr__, 'elastic_scattering', (0.1, 0.3))

    def testcutoff_energy_inelastic_eV(self):
        self.m.cutoff_energy_inelastic_eV = 123.45
        self.assertAlmostEqual(123.45, self.m.cutoff_energy_inelastic_eV, 4)

        self.assertRaises(ValueError, self.m.__setattr__, 'cutoff_energy_inelastic_eV', -1.0)

    def testcutoff_energy_bremsstrahlung_eV(self):
        self.m.cutoff_energy_bremsstrahlung_eV = 123.45
        self.assertAlmostEqual(123.45, self.m.cutoff_energy_bremsstrahlung_eV, 4)

        self.assertRaises(ValueError, self.m.__setattr__, 'cutoff_energy_bremsstrahlung_eV', -1.0)

    def testto_xml(self):
        element = mapper.to_xml(self.m)

        self.assertEquals('Pure Cu', element.get('name'))

        children = list(element.find('composition'))
        self.assertEqual(1, len(children))
        self.assertEqual(29, int(children[0].get('z')))

        self.assertAlmostEqual(8.96, float(element.get('density')) / 1000.0, 4)

        self.assertAlmostEqual(50, float(element.get('absorption_energy_electron')), 4)
        self.assertAlmostEqual(50, float(element.get('absorption_energy_photon')), 4)
        self.assertAlmostEqual(50, float(element.get('absorption_energy_positron')), 4)

        child = list(element.find('elastic_scattering'))[0]
        self.assertAlmostEqual(0.1, float(child.get('c1')), 4)
        self.assertAlmostEqual(0.2, float(child.get('c2')), 4)

        self.assertAlmostEqual(51.2, float(element.get('wcc')), 4)
        self.assertAlmostEqual(53.4, float(element.get('wcr')), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

