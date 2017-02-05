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
from pymontecarlo.options.detector.photon import PhotonDetector
from pymontecarlo.options.limit import ShowersLimit, UncertaintyLimit
from pymontecarlo.options.model import \
    ElasticCrossSectionModel, RUTHERFORD, ELSEPA2005, POUCHOU_PICHOIR1991
from pymontecarlo.options.analyses import PhotonIntensityAnalysis, KRatioAnalysis

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)
GERMANIUM = Material.pure(32)

class TestValidator(TestCase):

    def setUp(self):
        super().setUp()

        self.v = Validator()

        self.v.beam_validate_methods[GaussianBeam] = self.v._validate_beam_gaussian

        self.v.sample_validate_methods[SubstrateSample] = self.v._validate_sample_substrate
        self.v.sample_validate_methods[InclusionSample] = self.v._validate_sample_inclusion
        self.v.sample_validate_methods[HorizontalLayerSample] = self.v._validate_sample_horizontallayers
        self.v.sample_validate_methods[VerticalLayerSample] = self.v._validate_sample_verticallayers
        self.v.sample_validate_methods[SphereSample] = self.v._validate_sample_sphere

        self.v.detector_validate_methods[PhotonDetector] = self.v._validate_detector_photon

        self.v.limit_validate_methods[ShowersLimit] = self.v._validate_limit_showers
        self.v.limit_validate_methods[UncertaintyLimit] = self.v._validate_limit_uncertainty

        self.v.model_validate_methods[ElasticCrossSectionModel] = self.v._validate_model_valid_models

        self.v.analysis_validate_methods[PhotonIntensityAnalysis] = self.v._validate_analysis_photonintensity
        self.v.analysis_validate_methods[KRatioAnalysis] = self.v._validate_analysis_kratio

        self.v.valid_models[ElasticCrossSectionModel] = [ELSEPA2005]

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

    def testvalidate_detector_photon(self):
        detector = PhotonDetector(1.1, 2.2)
        detector2 = self.v.validate_detector(detector)
        self.assertEqual(detector2, detector)

    def testvalidate_detector_photon_exception(self):
        detector = PhotonDetector(2.0, -1.0)
        self.assertRaises(ValidationError, self.v.validate_detector, detector)

        errors = set()
        self.v._validate_detector(detector, errors)
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

    def testvalidate_model(self):
        model = ELSEPA2005
        model2 = self.v.validate_model(model)
        self.assertEqual(model2, model)

    def testvalidate_model_exception(self):
        model = RUTHERFORD
        self.assertRaises(ValidationError, self.v.validate_model, model)

        errors = set()
        self.v._validate_model(model, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_model_exception2(self):
        model = POUCHOU_PICHOIR1991
        self.assertRaises(ValidationError, self.v.validate_model, model)

        errors = set()
        self.v._validate_model(model, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_analysis_photonintensity(self):
        analysis = PhotonIntensityAnalysis()
        analysis2 = self.v.validate_analysis(analysis)
        self.assertEqual(analysis2, analysis)

    def testvalidate_analysis_kratio(self):
        analysis = KRatioAnalysis()
        analysis.add_standard_material(13, Material.pure(13))
        analysis2 = self.v.validate_analysis(analysis)
        self.assertEqual(analysis2, analysis)

    def testvalidate_analysis_kratio_exception(self):
        analysis = KRatioAnalysis()
        analysis.add_standard_material(14, Material.pure(13))
        self.assertRaises(ValidationError, self.v.validate_analysis, analysis)

        errors = set()
        self.v._validate_analysis(analysis, errors)
        self.assertEqual(1, len(errors))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
