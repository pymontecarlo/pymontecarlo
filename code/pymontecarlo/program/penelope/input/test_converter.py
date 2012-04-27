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

from pymontecarlo.program.penelope.input.converter import Converter
from pymontecarlo.input.options import Options
from pymontecarlo.input.geometry import \
    Substrate, Inclusion, MultiLayers, GrainBoundaries, Sphere
from pymontecarlo.input.body import Layer
from pymontecarlo.input.material import pure
from pymontecarlo.input.limit import TimeLimit

# Globals and constants variables.

class TestPenelopeConverter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.converter = Converter((0.1, 0.2), 51.2, 53.4)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test_convert_geometry_substrate(self):
        # Base options
        ops = Options(name="Test")
        ops.geometry = Substrate(pure(29))
        ops.limits.add(TimeLimit(100))

        # Convert
        self.converter._convert_geometry(ops)

        # Test
        self.assertEqual('Copper', str(ops.geometry.material))

        for material in ops.geometry.get_materials():
            self.assertAlmostEqual(0.1, material.elastic_scattering[0], 4)
            self.assertAlmostEqual(0.2, material.elastic_scattering[1], 4)
            self.assertAlmostEqual(51.2, material.cutoff_energy_inelastic_eV, 4)
            self.assertAlmostEqual(53.4, material.cutoff_energy_bremsstrahlung_eV, 4)

        for body in ops.geometry.get_bodies():
            self.assertAlmostEqual(1e20, body.maximum_step_length_m, 4)

    def test_convert_geometry_inclusion(self):
        # Base options
        ops = Options(name="Test")
        ops.geometry = Inclusion(pure(29), pure(30), 123.45)
        ops.limits.add(TimeLimit(100))

        # Convert
        self.converter._convert_geometry(ops)

        # Test
        self.assertEqual('Copper', str(ops.geometry.substrate_material))

        for material in ops.geometry.get_materials():
            self.assertAlmostEqual(0.1, material.elastic_scattering[0], 4)
            self.assertAlmostEqual(0.2, material.elastic_scattering[1], 4)
            self.assertAlmostEqual(51.2, material.cutoff_energy_inelastic_eV, 4)
            self.assertAlmostEqual(53.4, material.cutoff_energy_bremsstrahlung_eV, 4)

        for body in ops.geometry.get_bodies():
            self.assertAlmostEqual(1e20, body.maximum_step_length_m, 4)

    def test_convert_geometry_multilayers(self):
        # Base options
        ops = Options(name="Test")
        ops.geometry = MultiLayers(pure(29))
        ops.geometry.layers.append(Layer(pure(30), 12.34))
        ops.limits.add(TimeLimit(100))

        # Convert
        self.converter._convert_geometry(ops)

        # Test
        self.assertEqual('Copper', str(ops.geometry.substrate_material))
        self.assertEqual('Zinc', str(ops.geometry.layers[0].material))
        self.assertAlmostEqual(12.34, ops.geometry.layers[0].thickness_m, 4)

        for material in ops.geometry.get_materials():
            self.assertAlmostEqual(0.1, material.elastic_scattering[0], 4)
            self.assertAlmostEqual(0.2, material.elastic_scattering[1], 4)
            self.assertAlmostEqual(51.2, material.cutoff_energy_inelastic_eV, 4)
            self.assertAlmostEqual(53.4, material.cutoff_energy_bremsstrahlung_eV, 4)

        for layer in ops.geometry.layers:
            self.assertAlmostEqual(12.34 / 10.0, layer.maximum_step_length_m, 4)

    def test_convert_geometry_grainboundaries(self):
        # Base options
        ops = Options(name="Test")
        ops.geometry = GrainBoundaries(pure(29), pure(31))
        ops.geometry.layers.append(Layer(pure(30), 12.34))
        ops.limits.add(TimeLimit(100))

        # Convert
        self.converter._convert_geometry(ops)

        # Test
        self.assertEqual('Copper', str(ops.geometry.left_material))
        self.assertEqual('Gallium', str(ops.geometry.right_material))
        self.assertEqual('Zinc', str(ops.geometry.layers[0].material))
        self.assertAlmostEqual(12.34, ops.geometry.layers[0].thickness_m, 4)

        for material in ops.geometry.get_materials():
            self.assertAlmostEqual(0.1, material.elastic_scattering[0], 4)
            self.assertAlmostEqual(0.2, material.elastic_scattering[1], 4)
            self.assertAlmostEqual(51.2, material.cutoff_energy_inelastic_eV, 4)
            self.assertAlmostEqual(53.4, material.cutoff_energy_bremsstrahlung_eV, 4)

        for layer in ops.geometry.layers:
            self.assertAlmostEqual(12.34 / 10.0, layer.maximum_step_length_m, 4)

    def test_convert_geometry_sphere(self):
        # Base options
        ops = Options(name="Test")
        ops.geometry = Sphere(pure(29), 123.45)
        ops.limits.add(TimeLimit(100))

        # Convert
        self.converter._convert_geometry(ops)

        # Test
        self.assertEqual('Copper', str(ops.geometry.material))

        for material in ops.geometry.get_materials():
            self.assertAlmostEqual(0.1, material.elastic_scattering[0], 4)
            self.assertAlmostEqual(0.2, material.elastic_scattering[1], 4)
            self.assertAlmostEqual(51.2, material.cutoff_energy_inelastic_eV, 4)
            self.assertAlmostEqual(53.4, material.cutoff_energy_bremsstrahlung_eV, 4)

        for body in ops.geometry.get_bodies():
            self.assertAlmostEqual(1e20, body.maximum_step_length_m, 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
