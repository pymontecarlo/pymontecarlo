"""
Base validation.
"""

# Standard library modules.
import math

# Third party modules.
import pyxray.descriptor

import matplotlib.colors

# Local modules.
from pymontecarlo.exceptions import ValidationError
from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import \
    (SubstrateSample, InclusionSample, HorizontalLayerSample,
     VerticalLayerSample, SphereSample)
from pymontecarlo.options.sample.base import Layer
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.options.limit import ShowersLimit, UncertaintyLimit
from pymontecarlo.options.material import VACUUM
from pymontecarlo.options.particle import Particle
from pymontecarlo.util.xrayline import XrayLine

# Globals and constants variables.

class Validator(object):
    """
    Base validator of options and its components.
    
    Each validate method always takes two arguments:
        - object to be validated
        - :class:`set` to accumulate encountered errors
    """

    def __init__(self):
        self.beam_validate_methods = {}
        self.sample_validate_methods = {}
        self.analysis_validate_methods = {}
        self.limit_validate_methods = {}
        self.model_validate_methods = {}

        self.valid_models = {}
        self.default_models = {}

    def validate_options(self, options):
        errors = set()
        options = self._validate_options(options, errors)

        if errors:
            raise ValidationError(*errors)

        return options

    def _validate_options(self, options, errors):
        program = \
            self._validate_program(options.program, options, errors)
        beam = \
            self._validate_beam(options.beam, options, errors)
        sample = \
            self._validate_sample(options.sample, options, errors)
        analyses = \
            self._validate_analyses(options.analyses, options, errors)
        limits = \
            self._validate_limits(options.limits, options, errors)
        models = \
            self._validate_models(options.models, options, errors)

        return Options(program, beam, sample, analyses, limits, models)

    def validate_program(self, program, options):
        errors = set()
        program = self._validate_program(program, options, errors)

        if errors:
            raise ValidationError(*errors)

        return program

    def _validate_program(self, program, options, errors):
        return program

    def validate_beam(self, beam, options):
        errors = set()
        beam = self._validate_beam(beam, options, errors)

        if errors:
            raise ValidationError(*errors)

        return beam

    def _validate_beam(self, beam, options, errors):
        beam_class = beam.__class__
        if beam_class not in self.beam_validate_methods:
            exc = ValueError('Beam ({0}) is not supported.'
                             .format(beam_class.__name__))
            errors.add(exc)
            return beam

        method = self.beam_validate_methods[beam_class]
        return method(beam, options, errors)

    def _validate_beam_base_energy_eV(self, energy_eV, options, errors):
        if energy_eV <= 0.0:
            exc = ValueError('Energy ({0:g} eV) must be greater than 0.0.'
                             .format(energy_eV))
            errors.add(exc)

        return energy_eV

    def _validate_beam_base_particle(self, particle, options, errors):
        if particle not in Particle:
            exc = ValueError('Unknown particle: {0}.'.format(particle))
            errors.add(exc)

        return particle

    def _validate_beam_gaussian(self, beam, options, errors):
        energy_eV = \
            self._validate_beam_base_energy_eV(beam.energy_eV, options, errors)
        particle = \
            self._validate_beam_base_particle(beam.particle, options, errors)
        diameter_m = \
            self._validate_beam_gaussian_diameter_m(beam.diameter_m, options, errors)
        x0_m = \
            self._validate_beam_gaussian_x0_m(beam.x0_m, options, errors)
        y0_m = \
            self._validate_beam_gaussian_y0_m(beam.y0_m, options, errors)

        return GaussianBeam(energy_eV, diameter_m, particle, x0_m, y0_m)

    def _validate_beam_gaussian_diameter_m(self, diameter_m, options, errors):
        if diameter_m < 0.0:
            exc = ValueError('Diameter ({0:g} m) must be greater or equal to 0.0.'
                             .format(diameter_m))
            errors.add(exc)

        return diameter_m

    def _validate_beam_gaussian_x0_m(self, x0_m, options, errors):
        if not math.isfinite(x0_m):
            exc = ValueError('Initial x position must be a finite number.')
            errors.add(exc)

        return x0_m

    def _validate_beam_gaussian_y0_m(self, y0_m, options, errors):
        if not math.isfinite(y0_m):
            exc = ValueError('Initial y position must be a finite number.')
            errors.add(exc)

        return y0_m

    def validate_material(self, material, options):
        errors = set()
        material = self._validate_material(material, options, errors)

        if errors:
            raise ValidationError(*errors)

        return material

    def _validate_material(self, material, options, errors):
        if material is VACUUM:
            return material

        name = \
            self._validate_material_base_name(material.name, options, errors)
        composition = \
            self._validate_material_base_composition(material.composition, options, errors)
        density_kg_per_m3 = \
            self._validate_material_base_density_kg_per_m3(material.density_kg_per_m3, options, errors)
        color = \
            self._validate_material_base_color(material.color, options, errors)

        return Material(name, composition, density_kg_per_m3, color)

    def _validate_material_base_name(self, name, options, errors):
        name = name.strip()
        if not name:
            exc = ValueError('Name ({0:s}) must be at least one character.'
                             .format(name))
            errors.add(exc)

        return name

    def _validate_material_base_composition(self, composition, options, errors):
        outcomposition = {}

        for z, wf in composition.items():
            try:
                pyxray.descriptor.Element.validate(z)
            except ValueError as exc:
                errors.add(exc)
                continue

            if wf <= 0.0 or wf > 1.0:
                exc = ValueError('Weight fraction ({0:g}) must be between ]0.0, 1.0]')
                errors.add(exc)

            outcomposition[z] = wf

        total = sum(outcomposition.values())
        if not math.isclose(total, 1.0, abs_tol=Material.WEIGHT_FRACTION_TOLERANCE):
            exc = ValueError('Total weight fraction ({0:g}) does not equal 1.0.'
                             .format(total))
            errors.add(exc)

        return outcomposition

    def _validate_material_base_density_kg_per_m3(self, density_kg_per_m3, options, errors):
        if density_kg_per_m3 <= 0:
            exc = ValueError('Density ({0:g}kg/m3) must be greater or equal to 0.'
                             .format(density_kg_per_m3))
            errors.add(exc)

        return density_kg_per_m3

    def _validate_material_base_color(self, color, options, errors):
        if not matplotlib.colors.is_color_like(color):
            exc = ValueError('Color ({}) is not a valid color.'
                             .format(color))
            errors.add(exc)

        return color

    def validate_sample(self, sample, options):
        errors = set()
        sample = self._validate_sample(sample, options, errors)

        if errors:
            raise ValidationError(*errors)

        return sample

    def _validate_sample(self, sample, options, errors):
        sample_class = sample.__class__
        if sample_class not in self.sample_validate_methods:
            exc = ValueError('Sample ({0}) is not supported.'
                             .format(sample_class.__name__))
            errors.add(exc)
            return sample

        method = self.sample_validate_methods[sample_class]
        return method(sample, options, errors)

    def _validate_sample_base_tilt_rad(self, tilt_rad, options, errors):
        if not math.isfinite(tilt_rad):
            exc = ValueError('Tilt must be a finite number.')
            errors.add(exc)

        return tilt_rad

    def _validate_sample_base_azimuth_rad(self, azimuth_rad, options, errors):
        if not math.isfinite(azimuth_rad):
            exc = ValueError('Rotation must be a finite number.')
            errors.add(exc)

        return azimuth_rad

    def _validate_sample_substrate(self, sample, options, errors):
        material = \
            self._validate_sample_substrate_material(sample.material, options, errors)
        tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors)
        azimuth_rad = \
            self._validate_sample_base_azimuth_rad(sample.azimuth_rad, options, errors)

        return SubstrateSample(material, tilt_rad, azimuth_rad)

    def _validate_sample_substrate_material(self, material, options, errors):
        if material is VACUUM:
            exc = ValueError('Material cannot be VACUUM.')
            errors.add(exc)

        return self._validate_material(material, options, errors)

    def _validate_sample_inclusion(self, sample, options, errors):
        substrate_material = \
            self._validate_sample_inclusion_substrate_material(sample.substrate_material, options, errors)
        inclusion_material = \
            self._validate_sample_inclusion_inclusion_material(sample.inclusion_material, options, errors)
        inclusion_diameter_m = \
            self._validate_sample_inclusion_inclusion_diameter_m(sample.inclusion_diameter_m, options, errors)
        tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors)
        azimuth_rad = \
            self._validate_sample_base_azimuth_rad(sample.azimuth_rad, options, errors)

        return InclusionSample(substrate_material, inclusion_material, inclusion_diameter_m, tilt_rad, azimuth_rad)

    def _validate_sample_inclusion_substrate_material(self, material, options, errors):
        return self._validate_material(material, options, errors)

    def _validate_sample_inclusion_inclusion_material(self, material, options, errors):
        return self._validate_material(material, options, errors)

    def _validate_sample_inclusion_inclusion_diameter_m(self, diameter_m, options, errors):
        if diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0.'
                             .format(diameter_m))
            errors.add(exc)

        return diameter_m

    def _validate_sample_layered_layer(self, layer, options, errors):
        material = self._validate_material(layer.material, options, errors)

        if layer.thickness_m <= 0:
            exc = ValueError('Thickness ({0:g} m) must be greater than 0.'
                             .format(layer.thickness_m))
            errors.add(exc)

        return Layer(material, layer.thickness_m)

    def _validate_sample_layered_layers(self, layers, options, errors):
        outlayers = []

        for layer in layers:
            outlayer = self._validate_sample_layered_layer(layer, options, errors)
            outlayers.append(outlayer)

        return outlayers

    def _validate_sample_horizontallayers(self, sample, options, errors):
        substrate_material = \
            self._validate_sample_horizontallayers_substrate_material(sample.substrate_material, options, errors)
        layers = \
            self._validate_sample_horizontallayers_layers(sample.layers, options, errors)
        tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors)
        azimuth_rad = \
            self._validate_sample_base_azimuth_rad(sample.azimuth_rad, options, errors)

        return HorizontalLayerSample(substrate_material, layers, tilt_rad, azimuth_rad)

    def _validate_sample_horizontallayers_substrate_material(self, material, options, errors):
        return self._validate_material(material, options, errors)

    def _validate_sample_horizontallayers_layers(self, layers, options, errors):
        layers = self._validate_sample_layered_layers(layers, options, errors)

        if layers and layers[-1].material is VACUUM:
            layers.pop(-1)

        if not layers:
            exc = ValueError('At least one layer must be defined.')
            errors.add(ValueError(exc))

        return layers

    def _validate_sample_verticallayers(self, sample, options, errors):
        left_material = \
            self._validate_sample_verticallayers_left_material(sample.left_material, options, errors)
        right_material = \
            self._validate_sample_verticallayers_left_material(sample.right_material, options, errors)
        layers = \
            self._validate_sample_verticallayers_layers(sample.layers, options, errors)
        depth_m = \
            self._validate_sample_verticallayers_depth_m(sample.depth_m, options, errors)
        tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors)
        azimuth_rad = \
            self._validate_sample_base_azimuth_rad(sample.azimuth_rad, options, errors)

        return VerticalLayerSample(left_material, right_material, layers, depth_m, tilt_rad, azimuth_rad)

    def _validate_sample_verticallayers_left_material(self, material, options, errors):
        if material is VACUUM:
            exc = ValueError('Left material cannot be VACUUM.')
            errors.add(exc)

        return self._validate_material(material, options, errors)

    def _validate_sample_verticallayers_right_material(self, material, options, errors):
        if material is VACUUM:
            exc = ValueError('Right material cannot be VACUUM.')
            errors.add(exc)

        return self._validate_material(material, options, errors)

    def _validate_sample_verticallayers_layers(self, layers, options, errors):
        return self._validate_sample_layered_layers(layers, options, errors)

    def _validate_sample_verticallayers_depth_m(self, depth_m, options, errors):
        if depth_m <= 0.0:
            exc = ValueError('Depth ({0:g} m) must be greater than 0.'
                             .format(depth_m))
            errors.add(exc)

        return depth_m

    def _validate_sample_sphere(self, sample, options, errors):
        material = \
            self._validate_sample_sphere_material(sample.material, options, errors)
        diameter_m = \
            self._validate_sample_sphere_diameter_m(sample.diameter_m, options, errors)
        tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors)
        azimuth_rad = \
            self._validate_sample_base_azimuth_rad(sample.azimuth_rad, options, errors)

        return SphereSample(material, diameter_m, tilt_rad, azimuth_rad)

    def _validate_sample_sphere_material(self, material, options, errors):
        if material is VACUUM:
            exc = ValueError('Material cannot be VACUUM.')
            errors.add(exc)

        return self._validate_material(material, options, errors)

    def _validate_sample_sphere_diameter_m(self, diameter_m, options, errors):
        if diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0.'
                             .format(diameter_m))
            errors.add(exc)

        return diameter_m

    def _validate_detector_base_name(self, name, options, errors):
        name = name.strip()
        if not name:
            exc = ValueError('Name ({0:s}) must be at least one character.'
                             .format(name))
            errors.add(exc)

        return name

    def _validate_detector_photon(self, detector, options, errors):
        name = \
            self._validate_detector_base_name(detector.name, options, errors)
        elevation_rad = \
            self._validate_detector_photon_elevation_rad(detector.elevation_rad, options, errors)
        azimuth_rad = \
            self._validate_detector_photon_azimuth_rad(detector.azimuth_rad, options, errors)

        return PhotonDetector(name, elevation_rad, azimuth_rad)

    def _validate_detector_photon_elevation_rad(self, elevation_rad, options, errors):
        if elevation_rad < -math.pi / 2 or elevation_rad > math.pi / 2:
            exc = ValueError('Elevation ({0:g} rad) must be between [-pi/2,pi/2].'
                             .format(elevation_rad))
            errors.add(exc)

        return elevation_rad

    def _validate_detector_photon_azimuth_rad(self, azimuth_rad, options, errors):
        if azimuth_rad < 0 or azimuth_rad >= 2 * math.pi:
            exc = ValueError('Azimuth ({0:g} rad) must be between [0, 2pi[.'
                             .format(azimuth_rad))
            errors.add(exc)

        return azimuth_rad

    def validate_limits(self, limits, options):
        errors = set()
        limits = self._validate_limits(limits, options, errors)

        if errors:
            raise ValidationError(*errors)

        return limits

    def _validate_limits(self, limits, options, errors):
        if not limits:
            limits = options.program.create_default_limits(options)

        outlimits = []

        for limit in limits:
            outlimit = self._validate_limit(limit, options, errors)
            outlimits.append(outlimit)

        return outlimits

    def validate_limit(self, limit, options):
        errors = set()
        limit = self._validate_limit(limit, options, errors)

        if errors:
            raise ValidationError(*errors)

        return limit

    def _validate_limit(self, limit, options, errors):
        limit_class = limit.__class__
        if limit_class not in self.limit_validate_methods:
            exc = ValueError('Limit ({0}) is not supported.'
                             .format(limit_class.__name__))
            errors.add(exc)
            return limit

        method = self.limit_validate_methods[limit_class]
        return method(limit, options, errors)

    def _validate_limit_showers(self, limit, options, errors):
        showers = \
            self._validate_limit_showers_number_trajectories(limit.number_trajectories, options, errors)

        return ShowersLimit(showers)

    def _validate_limit_showers_number_trajectories(self, number_trajectories, options, errors):
        number_trajectories = int(number_trajectories)

        if number_trajectories <= 0:
            exc = ValueError('Number of trajectories ({0:d}) must be greater than 0.'
                             .format(number_trajectories))
            errors.add(exc)

        return number_trajectories

    def _validate_limit_uncertainty(self, limit, options, errors):
        xrayline = \
            self._validate_limit_uncertainty_xrayline(limit.xrayline, options, errors)
        detector = \
            self._validate_limit_uncertainty_detector(limit.detector, options, errors)
        uncertainty = \
            self._validate_limit_uncertainty_uncertainty(limit.uncertainty, options, errors)

        return UncertaintyLimit(xrayline, detector, uncertainty)

    def _validate_limit_uncertainty_xrayline(self, xrayline, options, errors):
        # Notes: No validate is required. Arguments are internally validated.
        return XrayLine(xrayline.element, xrayline.line)

    def _validate_limit_uncertainty_detector(self, detector, options, errors):
        return self._validate_detector_photon(detector, options, errors)

    def _validate_limit_uncertainty_uncertainty(self, uncertainty, options, errors):
        if uncertainty <= 0:
            exc = ValueError('Uncertainty ({0:g}) must be greater than 0.'
                             .format(uncertainty))
            errors.add(exc)

        return uncertainty

    def validate_models(self, models, options):
        errors = set()
        models = self._validate_models(models, options, errors)

        if errors:
            raise ValidationError(*errors)

        return models

    def _validate_models(self, models, options, errors):
        outmodels = []

        for model in models:
            outmodel = self._validate_model(model, options, errors)
            outmodels.append(outmodel)

        # Add default model if missing
        model_classes = set()
        for model in outmodels:
            model_classes.add(model.__class__)

        for model_class, default_model in self.default_models.items():
            if model_class not in model_classes:
                outmodels.append(default_model)

        return outmodels

    def validate_model(self, model, options):
        errors = set()
        model = self._validate_model(model, options, errors)

        if errors:
            raise ValidationError(*errors)

        return model

    def _validate_model(self, model, options, errors):
        model_class = model.__class__
        if model_class not in self.model_validate_methods:
            exc = ValueError('Model ({0}) is not supported.'
                             .format(model_class.__name__))
            errors.add(exc)
            return model

        method = self.model_validate_methods[model_class]
        return method(model, options, errors)

    def _validate_model_valid_models(self, model, options, errors):
        model_class = model.__class__
        if model not in self.valid_models.get(model_class, []):
            exc = ValueError('Model ({0}) is not supported.'.format(model))
            errors.add(exc)

        return model

    def validate_analyses(self, analyses, options):
        errors = set()
        analyses = self._validate_analyses(analyses, options, errors)

        if errors:
            raise ValidationError(*errors)

        return analyses

    def _validate_analyses(self, analyses, options, errors):
        outanalyses = []

        for analysis in analyses:
            outanalysis = self._validate_analysis(analysis, options, errors)
            outanalyses.append(outanalysis)

        return outanalyses

    def validate_analysis(self, analysis, options):
        errors = set()
        analysis = self._validate_analysis(analysis, options, errors)

        if errors:
            raise ValidationError(*errors)

        return analysis

    def _validate_analysis(self, analysis, options, errors):
        analysis_class = analysis.__class__
        if analysis_class not in self.analysis_validate_methods:
            exc = ValueError('Analysis ({0}) is not supported.'
                             .format(analysis_class.__name__))
            errors.add(exc)
            return analysis

        method = self.analysis_validate_methods[analysis_class]
        return method(analysis, options, errors)

    def _validate_analysis_photonintensity(self, analysis, options, errors):
        photon_detector = \
            self._validate_detector_photon(analysis.photon_detector, options, errors)

        return PhotonIntensityAnalysis(photon_detector)

    def _validate_analysis_kratio(self, analysis, options, errors):
        photon_detector = \
            self._validate_detector_photon(analysis.photon_detector, options, errors)
        standard_materials = \
            self._validate_analysis_kratio_standard_materials(analysis.standard_materials, options, errors)

        return KRatioAnalysis(photon_detector, standard_materials)

    def _validate_analysis_kratio_standard_materials(self, materials, options, errors):
        outmaterials = {}

        for z, material in materials.items():
            outmaterial = self._validate_material(material, options, errors)

            if z not in outmaterial.composition:
                exc = ValueError('Standard for element {0} does not have this element in its composition'
                                 .format(pyxray.element_symbol(z)))
                errors.add(exc)
                continue

            outmaterials[z] = outmaterial

        return outmaterials

