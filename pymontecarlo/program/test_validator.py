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
from pymontecarlo.options.model import ElasticCrossSectionModel, MassAbsorptionCoefficientModel
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.util.xrayline import XrayLine

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

        self.v.analysis_validate_methods[PhotonIntensityAnalysis] = self.v._validate_analysis_photonintensity
        self.v.analysis_validate_methods[KRatioAnalysis] = self.v._validate_analysis_kratio

        self.v.limit_validate_methods[ShowersLimit] = self.v._validate_limit_showers
        self.v.limit_validate_methods[UncertaintyLimit] = self.v._validate_limit_uncertainty

        self.v.model_validate_methods[ElasticCrossSectionModel] = self.v._validate_model_valid_models

        self.v.valid_models[ElasticCrossSectionModel] = [ElasticCrossSectionModel.ELSEPA2005]
        self.v.default_models[ElasticCrossSectionModel] = ElasticCrossSectionModel.ELSEPA2005

        self.options = self.create_basic_options()

    def testvalidate_material(self):
        material = Material('Pure Cu', {29: 1.0}, 8960.0)
        material2 = self.v.validate_material(material, self.options)
        self.assertEqual(material2, material)
        self.assertIsNot(material2, material)

    def testvalidate_material_exception(self):
        material = Material(' ', {120: 0.5}, -1.0, 'blah')
        self.assertRaises(ValidationError, self.v.validate_material, material, self.options)

        errors = set()
        self.v._validate_material(material, self.options, errors)
        self.assertEqual(5, len(errors))

    def testvalidate_beam_gaussian(self):
        beam = GaussianBeam(10e3, 0.123)
        beam2 = self.v.validate_beam(beam, self.options)
        self.assertEqual(beam2, beam)
        self.assertIsNot(beam2, beam)

    def testvalidate_beam_gaussian_exception(self):
        beam = GaussianBeam(0.0, -1.0, 'particle',
                            float('inf'), float('nan'))
        self.assertRaises(ValidationError, self.v.validate_beam, beam, self.options)

        errors = set()
        self.v._validate_beam(beam, self.options, errors)
        self.assertEqual(5, len(errors))

    def testvalidate_sample_substrate(self):
        sample = SubstrateSample(COPPER)
        sample2 = self.v.validate_sample(sample, self.options)
        self.assertEqual(sample2, sample)
        self.assertIsNot(sample2, sample)

    def testvalidate_sample_substrate_exception(self):
        sample = SubstrateSample(VACUUM, float('inf'), float('nan'))
        self.assertRaises(ValidationError, self.v.validate_sample, sample, self.options)

        errors = set()
        self.v._validate_sample(sample, self.options, errors)
        self.assertEqual(3, len(errors))

    def testvalidate_sample_inclusion(self):
        sample = InclusionSample(COPPER, ZINC, 1.0)
        sample2 = self.v.validate_sample(sample, self.options)
        self.assertEqual(sample2, sample)
        self.assertIsNot(sample2, sample)

    def testvalidate_sample_inclusion_exception(self):
        sample = InclusionSample(COPPER, ZINC, 0.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample, self.options)

        errors = set()
        self.v._validate_sample(sample, self.options, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_sample_horizontallayers(self):
        sample = HorizontalLayerSample(COPPER)
        sample.add_layer(ZINC, 1.0)
        sample2 = self.v.validate_sample(sample, self.options)
        self.assertEqual(sample2, sample)
        self.assertIsNot(sample2, sample)

    def testvalidate_sample_horizontallayers_empty_layer(self):
        sample = HorizontalLayerSample(COPPER)
        sample.add_layer(ZINC, 1.0)
        sample.add_layer(VACUUM, 2.0)
        sample2 = self.v.validate_sample(sample, self.options)
        self.assertEqual(1, len(sample2.layers))

    def testvalidate_sample_horizontallayers_exception(self):
        sample = HorizontalLayerSample(COPPER)
        sample.add_layer(ZINC, -1.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample, self.options)

        errors = set()
        self.v._validate_sample(sample, self.options, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_sample_verticallayers(self):
        sample = VerticalLayerSample(COPPER, ZINC)
        sample.add_layer(GALLIUM, 1.0)
        sample2 = self.v.validate_sample(sample, self.options)
        self.assertEqual(sample2, sample)
        self.assertIsNot(sample2, sample)

    def testvalidate_sample_verticallayers_exception(self):
        sample = VerticalLayerSample(VACUUM, VACUUM)
        sample.add_layer(GALLIUM, -1.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample, self.options)

        errors = set()
        self.v._validate_sample(sample, self.options, errors)
        self.assertEqual(3, len(errors))

    def testvalidate_sample_sphere(self):
        sample = SphereSample(COPPER, 1.0)
        sample2 = self.v.validate_sample(sample, self.options)
        self.assertEqual(sample2, sample)
        self.assertIsNot(sample2, sample)

    def testvalidate_sample_sphere_exception(self):
        sample = SphereSample(VACUUM, -1.0)
        self.assertRaises(ValidationError, self.v.validate_sample, sample, self.options)

        errors = set()
        self.v._validate_sample(sample, self.options, errors)
        self.assertEqual(2, len(errors))

    def testvalidate_analysis_photonintensity(self):
        detector = PhotonDetector('det', 1.1, 2.2)
        analysis = PhotonIntensityAnalysis(detector)
        analysis2 = self.v.validate_analysis(analysis, self.options)
        self.assertEqual(analysis2, analysis)
        self.assertIsNot(analysis2, analysis)

    def testvalidate_analysis_photonintensity_exception(self):
        detector = PhotonDetector('', 2.0, -1.0)
        analysis = PhotonIntensityAnalysis(detector)
        self.assertRaises(ValidationError, self.v.validate_analysis, analysis, self.options)

        errors = set()
        self.v._validate_analysis(analysis, self.options, errors)
        self.assertEqual(3, len(errors))

    def testvalidate_analysis_kratio(self):
        detector = PhotonDetector('det', 1.1, 2.2)
        analysis = KRatioAnalysis(detector)
        analysis.add_standard_material(13, Material.pure(13))
        analysis2 = self.v.validate_analysis(analysis, self.options)
        self.assertEqual(analysis2, analysis)
        self.assertIsNot(analysis2, analysis)

    def testvalidate_analysis_kratio_exception(self):
        detector = PhotonDetector('', 2.0, -1.0)
        analysis = KRatioAnalysis(detector)
        analysis.add_standard_material(14, Material.pure(13))
        self.assertRaises(ValidationError, self.v.validate_analysis, analysis, self.options)

        errors = set()
        self.v._validate_analysis(analysis, self.options, errors)
        self.assertEqual(4, len(errors))

    def testvalidate_limit_showers(self):
        limit = ShowersLimit(1000)
        limit2 = self.v.validate_limit(limit, self.options)
        self.assertEqual(limit2, limit)
        self.assertIsNot(limit2, limit)

    def testvalidate_limit_showers_exception(self):
        limit = ShowersLimit(0)
        self.assertRaises(ValidationError, self.v.validate_limit, limit, self.options)

        errors = set()
        self.v._validate_limit(limit, self.options, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_limit_uncertainty(self):
        xrayline = XrayLine(13, 'Ka1')
        detector = PhotonDetector('det', 1.1, 2.2)
        limit = UncertaintyLimit(xrayline, detector, 0.02)
        limit2 = self.v.validate_limit(limit, self.options)
        self.assertEqual(limit2, limit)
        self.assertIsNot(limit2, limit)

    def testvalidate_limit_uncertainty_exception(self):
        xrayline = XrayLine(13, 'Ka1')
        detector = PhotonDetector('', float('nan'), -1)
        limit = UncertaintyLimit(xrayline, detector, 0.0)
        self.assertRaises(ValidationError, self.v.validate_limit, limit, self.options)

        errors = set()
        self.v._validate_limit(limit, self.options, errors)
        self.assertEqual(3, len(errors))

    def testvalidate_models(self):
        models = [ElasticCrossSectionModel.ELSEPA2005]
        models2 = self.v.validate_models(models, self.options)
        self.assertSequenceEqual(models2, models)

    def testvalidate_models_exception(self):
        models = [ElasticCrossSectionModel.RUTHERFORD]
        self.assertRaises(ValidationError, self.v.validate_models, models, self.options)

        errors = set()
        self.v._validate_models(models, self.options, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_models_default(self):
        models = []
        models2 = self.v.validate_models(models, self.options)
        self.assertSequenceEqual(models2, [ElasticCrossSectionModel.ELSEPA2005])

    def testvalidate_model(self):
        model = ElasticCrossSectionModel.ELSEPA2005
        model2 = self.v.validate_model(model, self.options)
        self.assertEqual(model2, model)
        self.assertIs(model2, model)

    def testvalidate_model_exception(self):
        model = ElasticCrossSectionModel.RUTHERFORD
        self.assertRaises(ValidationError, self.v.validate_model, model, self.options)

        errors = set()
        self.v._validate_model(model, self.options, errors)
        self.assertEqual(1, len(errors))

    def testvalidate_model_exception2(self):
        model = MassAbsorptionCoefficientModel.POUCHOU_PICHOIR1991
        self.assertRaises(ValidationError, self.v.validate_model, model, self.options)

        errors = set()
        self.v._validate_model(model, self.options, errors)
        self.assertEqual(1, len(errors))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
