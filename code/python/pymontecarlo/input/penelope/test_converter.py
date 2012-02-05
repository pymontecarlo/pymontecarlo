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
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.input.penelope.converter import Converter
from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.beam import PencilBeam
from pymontecarlo.input.base.geometry import Inclusion, MultiLayers, GrainBoundaries
from pymontecarlo.input.base.body import Layer
from pymontecarlo.input.base.material import pure

# Globals and constants variables.
warnings.simplefilter("always")

class TestPenelopeConverter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.converter = Converter((0.1, 0.2), 51.2, 53.4)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testconvert1(self):
        # Base options
        ops = Options(name="Test")
        ops.beam = PencilBeam(1234)

        # Convert
        with warnings.catch_warnings(record=True) as ws:
            self.converter.convert(ops)

        # 1 warning:
        # PencilBeam -> GaussianBeam
        # Set default models (6)
        self.assertEqual(7, len(ws))

        # Test
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)
        self.assertAlmostEqual(0.0, ops.beam.diameter_m, 4)

        for material in ops.geometry.get_materials():
            self.assertAlmostEqual(0.1, material.elastic_scattering[0], 4)
            self.assertAlmostEqual(0.2, material.elastic_scattering[1], 4)
            self.assertAlmostEqual(51.2, material.cutoff_energy_inelastic_eV, 4)
            self.assertAlmostEqual(53.4, material.cutoff_energy_bremsstrahlung_eV, 4)

        for body in ops.geometry.get_bodies():
            self.assertAlmostEqual(1e20, body.maximum_step_length_m, 4)

        self.assertEqual(6, len(ops.models))

    def testconvert2(self):
        # Base options
        ops = Options(name="Test")
        ops.geometry = Inclusion(pure(29), pure(30), 123.45)

        # Convert
        self.converter.convert(ops)

        # Test
        self.assertEqual('Copper', str(ops.geometry.substrate_material))

        for material in ops.geometry.get_materials():
            self.assertAlmostEqual(0.1, material.elastic_scattering[0], 4)
            self.assertAlmostEqual(0.2, material.elastic_scattering[1], 4)
            self.assertAlmostEqual(51.2, material.cutoff_energy_inelastic_eV, 4)
            self.assertAlmostEqual(53.4, material.cutoff_energy_bremsstrahlung_eV, 4)

        for body in ops.geometry.get_bodies():
            self.assertAlmostEqual(1e20, body.maximum_step_length_m, 4)

        self.assertEqual(6, len(ops.models))

    def testconvert3(self):
        # Base options
        ops = Options(name="Test")
        ops.geometry = MultiLayers(pure(29))
        ops.geometry.layers.append(Layer(pure(30), 12.34))

        # Convert
        self.converter.convert(ops)

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

        self.assertEqual(6, len(ops.models))

    def testconvert4(self):
        # Base options
        ops = Options(name="Test")
        ops.geometry = GrainBoundaries(pure(29), pure(31))
        ops.geometry.layers.append(Layer(pure(30), 12.34))

        # Convert
        self.converter.convert(ops)

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

        self.assertEqual(6, len(ops.models))


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
