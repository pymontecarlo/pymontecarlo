#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.exceptions import ValidationError
from pymontecarlo.program.validator import Validator
from pymontecarlo.options.material import Material, VACUUM
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import \
    (SubstrateSample, InclusionSample, HorizontalLayerSample,
     VerticalLayerSample, SphereSample)
from pymontecarlo.options.limit import ShowersLimit, UncertaintyLimit

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
        material2 = self.v.validate_material(material)
        self.assertEqual(material2, material)

    def testvalidate_material_exception(self):
        material = Material(' ', {120: 0.5}, -1.0)
        self.assertRaises(ValidationError, self.v.validate_material, material)

        errors = set()
        self.v._validate_material(material, errors)
        self.assertEqual(4, len(errors))

    def testvalidate_beam_gaussian(self):
        beam = GaussianBeam(10e3, 0.123)
        beam2 = self.v.validate_beam(beam)
        self.assertEqual(beam2, beam)

    def testvalidate_beam_gaussian_exception(self):
        beam = GaussianBeam(0.0, -1.0, 'particle',
                            float('inf'), float('nan'),
                            float('inf'), float('nan'))
        self.assertRaises(ValidationError, self.v.validate_beam, beam)

        errors = set()
        self.v._validate_beam(beam, errors)
        self.assertEqual(7, len(errors))

    def testvalidate_sample_substrate(self):
        sample = SubstrateSample(COPPER)
        sample2 = self.v.validate_sample(sample)
        self.assertEqual(sample2, sample)

    def testvalidate_sample_substrate_exception(self):
        sample = SubstrateSample(VACUUM, float('inf'), float('nan'))
        self.assertRaises(ValidationError, self.v.validate_sample, sample)

        errors = set()
        self.v._validate_sample(sample, errors)
        self.assertEqual(3, len(errors))

    def testvalidate_sample_inclusion(self):
        sample = InclusionSample(COPPER, ZINC, 1.0)
        sample2 = self.v.validate_sample(sample)
        self.assertEqual(sample2, sample)

    def testvalidate_sample_inclusion_exception(self):
        sample = InclusionSample(COPPER, ZINC, 0.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample)

        errors = set()
        self.v._validate_sample(sample, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_sample_horizontallayers(self):
        sample = HorizontalLayerSample(COPPER)
        sample.add_layer(ZINC, 1.0)
        sample2 = self.v.validate_sample(sample)
        self.assertEqual(sample2, sample)

    def testvalidate_sample_horizontallayers_empty_layer(self):
        sample = HorizontalLayerSample(COPPER)
        sample.add_layer(ZINC, 1.0)
        sample.add_layer(VACUUM, 2.0)
        self.v.validate_sample(sample)
        self.assertEqual(1, len(sample.layers))

    def testvalidate_sample_horizontallayers_exception(self):
        sample = HorizontalLayerSample(COPPER)
        sample.add_layer(ZINC, -1.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample)

        errors = set()
        self.v._validate_sample(sample, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_sample_verticallayers(self):
        sample = VerticalLayerSample(COPPER, ZINC)
        sample.add_layer(GALLIUM, 1.0)
        sample2 = self.v.validate_sample(sample)
        self.assertEqual(sample2, sample)

    def testvalidate_sample_verticallayers_exception(self):
        sample = VerticalLayerSample(VACUUM, VACUUM)
        sample.add_layer(GALLIUM, -1.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample)

        errors = set()
        self.v._validate_sample(sample, errors)
        self.assertEqual(3, len(errors))

    def testvalidate_sample_sphere(self):
        sample = SphereSample(COPPER, 1.0)
        sample2 = self.v.validate_sample(sample)
        self.assertEqual(sample2, sample)

    def testvalidate_sample_sphere_exception(self):
        sample = SphereSample(VACUUM, -1.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample)

        errors = set()
        self.v._validate_sample(sample, errors)
        self.assertEqual(2, len(errors))

    def testvalidate_limit_showers(self):
        limit = ShowersLimit(1000)
        limit2 = self.v.validate_limit(limit)
        self.assertEqual(limit2, limit)

    def testvalidate_limit_showers_exception(self):
        limit = ShowersLimit(0)
        self.assertRaises(ValidationError, self.v.validate_limit, limit)

        errors = set()
        self.v._validate_limit(limit, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_limit_uncertainty(self):
        limit = UncertaintyLimit(13, 'Ka1', None, 0.02)
        limit2 = self.v.validate_limit(limit)
        self.assertEqual(limit2, limit)

    def testvalidate_limit_uncertainty_exception(self):
        limit = UncertaintyLimit(-1, 'Ka1', None, 0.0)
        self.assertRaises(ValidationError, self.v.validate_limit, limit)

        errors = set()
        self.v._validate_limit(limit, errors)
        self.assertEqual(2, len(errors))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
