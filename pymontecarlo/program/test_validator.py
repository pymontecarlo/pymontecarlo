#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.program.validator import Validator
from pymontecarlo.options.material import Material, VACUUM
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import \
    Substrate, Inclusion, HorizontalLayers, VerticalLayers, Sphere
from pymontecarlo.exceptions import ValidationError

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)
GERMANIUM = Material.pure(32)

class TestValidator(TestCase):

    def setUp(self):
        super().setUp()

        self.v = Validator()

    def testvalidate_material(self):
        material = Material('Pure Cu', {29: 1.0}, 8960.0)
        self.v.validate_material(material)

    def testvalidate_material_exception(self):
        material = Material(' ', {120: 0.5}, -1.0)
        self.assertRaises(ValidationError, self.v.validate_material, material)

        errors = set()
        self.v._validate_material(material, errors)
        self.assertEqual(4, len(errors))

    def testvalidate_beam_gaussian(self):
        beam = GaussianBeam(10e3, 0.123)
        self.v.validate_beam(beam)

    def testvalidate_beam_gaussian_exception(self):
        beam = GaussianBeam(0.0, -1.0, 'particle',
                            float('inf'), float('nan'),
                            float('inf'), float('nan'))
        self.assertRaises(ValidationError, self.v.validate_beam, beam)

        errors = set()
        self.v._validate_beam(beam, errors)
        self.assertEqual(7, len(errors))

    def testvalidate_sample_substrate(self):
        sample = Substrate(COPPER)
        self.v.validate_sample(sample)

    def testvalidate_sample_substrate_exception(self):
        sample = Substrate(VACUUM, float('inf'), float('nan'))
        self.assertRaises(ValidationError, self.v.validate_sample, sample)

        errors = set()
        self.v._validate_sample(sample, errors)
        self.assertEqual(3, len(errors))

    def testvalidate_sample_inclusion(self):
        sample = Inclusion(COPPER, ZINC, 1.0)
        self.v.validate_sample(sample)

    def testvalidate_sample_inclusion_exception(self):
        sample = Inclusion(COPPER, ZINC, 0.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample)

        errors = set()
        self.v._validate_sample(sample, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_sample_horizontallayers(self):
        sample = HorizontalLayers(COPPER)
        sample.add_layer(ZINC, 1.0)
        self.v.validate_sample(sample)

    def testvalidate_sample_horizontallayers_empty_layer(self):
        sample = HorizontalLayers(COPPER)
        sample.add_layer(ZINC, 1.0)
        sample.add_layer(VACUUM, 2.0)
        self.v.validate_sample(sample)
        self.assertEqual(1, len(sample.layers))

    def testvalidate_sample_horizontallayers_exception(self):
        sample = HorizontalLayers(COPPER)
        sample.add_layer(ZINC, -1.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample)

        errors = set()
        self.v._validate_sample(sample, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_sample_verticallayers(self):
        sample = VerticalLayers(COPPER, ZINC)
        sample.add_layer(GALLIUM, 1.0)
        self.v.validate_sample(sample)

    def testvalidate_sample_verticallayers_exception(self):
        sample = VerticalLayers(VACUUM, VACUUM)
        sample.add_layer(GALLIUM, -1.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample)

        errors = set()
        self.v._validate_sample(sample, errors)
        self.assertEqual(3, len(errors))

    def testvalidate_sample_sphere(self):
        sample = Sphere(COPPER, 1.0)
        self.v.validate_sample(sample)

    def testvalidate_sample_sphere_exception(self):
        sample = Sphere(VACUUM, -1.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample)

        errors = set()
        self.v._validate_sample(sample, errors)
        self.assertEqual(2, len(errors))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
