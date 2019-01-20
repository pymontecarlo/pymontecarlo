"""
Base validation.
"""

# Standard library modules.
import abc
import math
import warnings as warnings_module

# Third party modules.
import pyxray.descriptor

import matplotlib.colors

# Local modules.
from pymontecarlo.exceptions import ValidationError, ValidationWarning
from pymontecarlo.options.options import Options
from pymontecarlo.options.beam.gaussian import GaussianBeam
from pymontecarlo.options.beam.cylindrical import CylindricalBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import \
    (SubstrateSample, InclusionSample, HorizontalLayerSample,
     VerticalLayerSample, SphereSample)
from pymontecarlo.options.sample.base import Layer
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.options.material import VACUUM
from pymontecarlo.options.particle import Particle
from pymontecarlo.options.composition import calculate_density_kg_per_m3

# Globals and constants variables.

class ValidatorBase(metaclass=abc.ABCMeta):
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
        self.valid_models = {}

    def validate_options(self, options):
        errors = set()
        warnings = set()
        options = self._validate_options(options, errors, warnings)

        if errors:
            raise ValidationError(*errors)

        if warnings:
            warning = ValidationWarning(*warnings)
            warnings_module.warn(warning)

        return options

    def _validate_options(self, options, errors, warnings):
        program = \
            self._validate_program(options.program, options, errors, warnings)
        beam = \
            self._validate_beam(options.beam, options, errors, warnings)
        sample = \
            self._validate_sample(options.sample, options, errors, warnings)
        analyses = \
            self._validate_analyses(options.analyses, options, errors, warnings)
        tags = \
            self._validate_tags(options.tags, options, errors, warnings)

        return Options(program, beam, sample, analyses, tags)

    def validate_program(self, program, options):
        errors = set()
        warnings = set()
        program = self._validate_program(program, options, errors, warnings)

        if errors:
            raise ValidationError(*errors)

        if warnings:
            warning = ValidationWarning(*warnings)
            warnings_module.warn(warning)

        return program

    @abc.abstractmethod
    def _validate_program(self, program, options, errors, warnings):
        raise NotImplementedError

    def _validate_model(self, model, options, errors, warnings):
        model_class = model.__class__
        if model not in self.valid_models.get(model_class, []):
            exc = ValueError('Model ({0}) is not supported.'.format(model))
            errors.add(exc)

        return model

    def validate_beam(self, beam, options):
        errors = set()
        warnings = set()
        beam = self._validate_beam(beam, options, errors, warnings)

        if errors:
            raise ValidationError(*errors)

        if warnings:
            warning = ValidationWarning(*warnings)
            warnings_module.warn(warning)

        return beam

    def _validate_beam(self, beam, options, errors, warnings):
        beam_class = beam.__class__
        if beam_class not in self.beam_validate_methods:
            exc = ValueError('Beam ({0}) is not supported.'
                             .format(beam_class.__name__))
            errors.add(exc)
            return beam

        method = self.beam_validate_methods[beam_class]
        return method(beam, options, errors, warnings)

    def _validate_beam_base_energy_eV(self, energy_eV, options, errors, warnings):
        if energy_eV <= 0.0:
            exc = ValueError('Energy ({0:g} eV) must be greater than 0.0.'
                             .format(energy_eV))
            errors.add(exc)

        return energy_eV

    def _validate_beam_base_particle(self, particle, options, errors, warnings):
        if not isinstance(particle, Particle):
            exc = ValueError('Unknown particle: {0}.'.format(particle))
            errors.add(exc)

        return particle

    def _validate_beam_cylindrical(self, beam, options, errors, warnings):
        energy_eV = \
            self._validate_beam_base_energy_eV(beam.energy_eV, options, errors, warnings)
        particle = \
            self._validate_beam_base_particle(beam.particle, options, errors, warnings)
        diameter_m = \
            self._validate_beam_cylindrical_diameter_m(beam.diameter_m, options, errors, warnings)
        x0_m = \
            self._validate_beam_cylindrical_x0_m(beam.x0_m, options, errors, warnings)
        y0_m = \
            self._validate_beam_cylindrical_y0_m(beam.y0_m, options, errors, warnings)

        return CylindricalBeam(energy_eV, diameter_m, particle, x0_m, y0_m)

    def _validate_beam_cylindrical_diameter_m(self, diameter_m, options, errors, warnings):
        if diameter_m < 0.0:
            exc = ValueError('Diameter ({0:g} m) must be greater or equal to 0.0.'
                             .format(diameter_m))
            errors.add(exc)

        return diameter_m

    def _validate_beam_cylindrical_x0_m(self, x0_m, options, errors, warnings):
        if not math.isfinite(x0_m):
            exc = ValueError('Initial x position must be a finite number.')
            errors.add(exc)

        return x0_m

    def _validate_beam_cylindrical_y0_m(self, y0_m, options, errors, warnings):
        if not math.isfinite(y0_m):
            exc = ValueError('Initial y position must be a finite number.')
            errors.add(exc)

        return y0_m

    def _validate_beam_gaussian(self, beam, options, errors, warnings):
        energy_eV = \
            self._validate_beam_base_energy_eV(beam.energy_eV, options, errors, warnings)
        particle = \
            self._validate_beam_base_particle(beam.particle, options, errors, warnings)
        diameter_m = \
            self._validate_beam_gaussian_diameter_m(beam.diameter_m, options, errors, warnings)
        x0_m = \
            self._validate_beam_gaussian_x0_m(beam.x0_m, options, errors, warnings)
        y0_m = \
            self._validate_beam_gaussian_y0_m(beam.y0_m, options, errors, warnings)

        return GaussianBeam(energy_eV, diameter_m, particle, x0_m, y0_m)

    def _validate_beam_gaussian_diameter_m(self, diameter_m, options, errors, warnings):
        if diameter_m < 0.0:
            exc = ValueError('Diameter ({0:g} m) must be greater or equal to 0.0.'
                             .format(diameter_m))
            errors.add(exc)

        return diameter_m

    def _validate_beam_gaussian_x0_m(self, x0_m, options, errors, warnings):
        if not math.isfinite(x0_m):
            exc = ValueError('Initial x position must be a finite number.')
            errors.add(exc)

        return x0_m

    def _validate_beam_gaussian_y0_m(self, y0_m, options, errors, warnings):
        if not math.isfinite(y0_m):
            exc = ValueError('Initial y position must be a finite number.')
            errors.add(exc)

        return y0_m

    def validate_material(self, material, options):
        errors = set()
        warnings = set()
        material = self._validate_material(material, options, errors, warnings)

        if errors:
            raise ValidationError(*errors)

        if warnings:
            warning = ValidationWarning(*warnings)
            warnings_module.warn(warning)

        return material

    def _validate_material(self, material, options, errors, warnings):
        if material is VACUUM:
            return material

        name = \
            self._validate_material_base_name(material.name, options, errors, warnings)
        composition = \
            self._validate_material_base_composition(material.composition, options, errors, warnings)
        density_kg_per_m3 = \
            self._validate_material_base_density_kg_per_m3(material.density_kg_per_m3, material, options, errors, warnings)
        color = \
            self._validate_material_base_color(material.color, options, errors, warnings)

        return Material(name, composition, density_kg_per_m3, color)

    def _validate_material_base_name(self, name, options, errors, warnings):
        name = name.strip()
        if not name:
            exc = ValueError('Name ({0:s}) must be at least one character.'
                             .format(name))
            errors.add(exc)

        return name

    def _validate_material_base_composition(self, composition, options, errors, warnings):
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

    def _validate_material_base_density_kg_per_m3(self, density_kg_per_m3, material, options, errors, warnings):
        if density_kg_per_m3 is None:
            density_kg_per_m3 = calculate_density_kg_per_m3(material.composition)
            warning = RuntimeWarning('Density for {} was calculated as {:g}kg/m3'
                                     .format(material.name, density_kg_per_m3))
            warnings.add(warning)

        if density_kg_per_m3 <= 0:
            exc = ValueError('Density ({0:g}kg/m3) must be greater or equal to 0.'
                             .format(density_kg_per_m3))
            errors.add(exc)

        return density_kg_per_m3

    def _validate_material_base_color(self, color, options, errors, warnings):
        if not matplotlib.colors.is_color_like(color):
            exc = ValueError('Color ({}) is not a valid color.'
                             .format(color))
            errors.add(exc)

        return color

    def validate_sample(self, sample, options):
        errors = set()
        warnings = set()
        sample = self._validate_sample(sample, options, errors, warnings)

        if errors:
            raise ValidationError(*errors)

        if warnings:
            warning = ValidationWarning(*warnings)
            warnings_module.warn(warning)

        return sample

    def _validate_sample(self, sample, options, errors, warnings):
        sample_class = sample.__class__
        if sample_class not in self.sample_validate_methods:
            exc = ValueError('Sample ({0}) is not supported.'
                             .format(sample_class.__name__))
            errors.add(exc)
            return sample

        method = self.sample_validate_methods[sample_class]
        return method(sample, options, errors, warnings)

    def _validate_sample_base_tilt_rad(self, tilt_rad, options, errors, warnings):
        if not math.isfinite(tilt_rad):
            exc = ValueError('Tilt must be a finite number.')
            errors.add(exc)

        return tilt_rad

    def _validate_sample_base_azimuth_rad(self, azimuth_rad, options, errors, warnings):
        if not math.isfinite(azimuth_rad):
            exc = ValueError('Rotation must be a finite number.')
            errors.add(exc)

        return azimuth_rad

    def _validate_sample_substrate(self, sample, options, errors, warnings):
        material = \
            self._validate_sample_substrate_material(sample.material, options, errors, warnings)
        tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors, warnings)
        azimuth_rad = \
            self._validate_sample_base_azimuth_rad(sample.azimuth_rad, options, errors, warnings)

        return SubstrateSample(material, tilt_rad, azimuth_rad)

    def _validate_sample_substrate_material(self, material, options, errors, warnings):
        if material is VACUUM:
            exc = ValueError('Material cannot be VACUUM.')
            errors.add(exc)

        return self._validate_material(material, options, errors, warnings)

    def _validate_sample_inclusion(self, sample, options, errors, warnings):
        substrate_material = \
            self._validate_sample_inclusion_substrate_material(sample.substrate_material, options, errors, warnings)
        inclusion_material = \
            self._validate_sample_inclusion_inclusion_material(sample.inclusion_material, options, errors, warnings)
        inclusion_diameter_m = \
            self._validate_sample_inclusion_inclusion_diameter_m(sample.inclusion_diameter_m, options, errors, warnings)
        tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors, warnings)
        azimuth_rad = \
            self._validate_sample_base_azimuth_rad(sample.azimuth_rad, options, errors, warnings)

        return InclusionSample(substrate_material, inclusion_material, inclusion_diameter_m, tilt_rad, azimuth_rad)

    def _validate_sample_inclusion_substrate_material(self, material, options, errors, warnings):
        return self._validate_material(material, options, errors, warnings)

    def _validate_sample_inclusion_inclusion_material(self, material, options, errors, warnings):
        return self._validate_material(material, options, errors, warnings)

    def _validate_sample_inclusion_inclusion_diameter_m(self, diameter_m, options, errors, warnings):
        if diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0.'
                             .format(diameter_m))
            errors.add(exc)

        return diameter_m

    def _validate_sample_layered_layer(self, layer, options, errors, warnings):
        material = self._validate_material(layer.material, options, errors, warnings)

        if layer.thickness_m <= 0:
            exc = ValueError('Thickness ({0:g} m) must be greater than 0.'
                             .format(layer.thickness_m))
            errors.add(exc)

        return Layer(material, layer.thickness_m)

    def _validate_sample_layered_layers(self, layers, options, errors, warnings):
        outlayers = []

        for layer in layers:
            outlayer = self._validate_sample_layered_layer(layer, options, errors, warnings)
            outlayers.append(outlayer)

        return outlayers

    def _validate_sample_horizontallayers(self, sample, options, errors, warnings):
        substrate_material = \
            self._validate_sample_horizontallayers_substrate_material(sample.substrate_material, options, errors, warnings)
        layers = \
            self._validate_sample_horizontallayers_layers(sample.layers, options, errors, warnings)
        tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors, warnings)
        azimuth_rad = \
            self._validate_sample_base_azimuth_rad(sample.azimuth_rad, options, errors, warnings)

        return HorizontalLayerSample(substrate_material, layers, tilt_rad, azimuth_rad)

    def _validate_sample_horizontallayers_substrate_material(self, material, options, errors, warnings):
        return self._validate_material(material, options, errors, warnings)

    def _validate_sample_horizontallayers_layers(self, layers, options, errors, warnings):
        layers = self._validate_sample_layered_layers(layers, options, errors, warnings)

        if layers and layers[-1].material is VACUUM:
            layers.pop(-1)

        if not layers:
            exc = ValueError('At least one layer must be defined.')
            errors.add(ValueError(exc))

        return layers

    def _validate_sample_verticallayers(self, sample, options, errors, warnings):
        left_material = \
            self._validate_sample_verticallayers_left_material(sample.left_material, options, errors, warnings)
        right_material = \
            self._validate_sample_verticallayers_left_material(sample.right_material, options, errors, warnings)
        layers = \
            self._validate_sample_verticallayers_layers(sample.layers, options, errors, warnings)
        depth_m = \
            self._validate_sample_verticallayers_depth_m(sample.depth_m, options, errors, warnings)
        tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors, warnings)
        azimuth_rad = \
            self._validate_sample_base_azimuth_rad(sample.azimuth_rad, options, errors, warnings)

        return VerticalLayerSample(left_material, right_material, layers, depth_m, tilt_rad, azimuth_rad)

    def _validate_sample_verticallayers_left_material(self, material, options, errors, warnings):
        if material is VACUUM:
            exc = ValueError('Left material cannot be VACUUM.')
            errors.add(exc)

        return self._validate_material(material, options, errors, warnings)

    def _validate_sample_verticallayers_right_material(self, material, options, errors, warnings):
        if material is VACUUM:
            exc = ValueError('Right material cannot be VACUUM.')
            errors.add(exc)

        return self._validate_material(material, options, errors, warnings)

    def _validate_sample_verticallayers_layers(self, layers, options, errors, warnings):
        return self._validate_sample_layered_layers(layers, options, errors, warnings)

    def _validate_sample_verticallayers_depth_m(self, depth_m, options, errors, warnings):
        if depth_m <= 0.0:
            exc = ValueError('Depth ({0:g} m) must be greater than 0.'
                             .format(depth_m))
            errors.add(exc)

        return depth_m

    def _validate_sample_sphere(self, sample, options, errors, warnings):
        material = \
            self._validate_sample_sphere_material(sample.material, options, errors, warnings)
        diameter_m = \
            self._validate_sample_sphere_diameter_m(sample.diameter_m, options, errors, warnings)
        tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors, warnings)
        azimuth_rad = \
            self._validate_sample_base_azimuth_rad(sample.azimuth_rad, options, errors, warnings)

        return SphereSample(material, diameter_m, tilt_rad, azimuth_rad)

    def _validate_sample_sphere_material(self, material, options, errors, warnings):
        if material is VACUUM:
            exc = ValueError('Material cannot be VACUUM.')
            errors.add(exc)

        return self._validate_material(material, options, errors, warnings)

    def _validate_sample_sphere_diameter_m(self, diameter_m, options, errors, warnings):
        if diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0.'
                             .format(diameter_m))
            errors.add(exc)

        return diameter_m

    def _validate_detector_base_name(self, name, options, errors, warnings):
        name = name.strip()
        if not name:
            exc = ValueError('Name ({0:s}) must be at least one character.'
                             .format(name))
            errors.add(exc)

        return name

    def _validate_detector_photon(self, detector, options, errors, warnings):
        name = \
            self._validate_detector_base_name(detector.name, options, errors, warnings)
        elevation_rad = \
            self._validate_detector_photon_elevation_rad(detector.elevation_rad, options, errors, warnings)
        azimuth_rad = \
            self._validate_detector_photon_azimuth_rad(detector.azimuth_rad, options, errors, warnings)

        return PhotonDetector(name, elevation_rad, azimuth_rad)

    def _validate_detector_photon_elevation_rad(self, elevation_rad, options, errors, warnings):
        if elevation_rad < -math.pi / 2 or elevation_rad > math.pi / 2:
            exc = ValueError('Elevation ({0:g} rad) must be between [-pi/2,pi/2].'
                             .format(elevation_rad))
            errors.add(exc)

        return elevation_rad

    def _validate_detector_photon_azimuth_rad(self, azimuth_rad, options, errors, warnings):
        if azimuth_rad < 0 or azimuth_rad >= 2 * math.pi:
            exc = ValueError('Azimuth ({0:g} rad) must be between [0, 2pi[.'
                             .format(azimuth_rad))
            errors.add(exc)

        return azimuth_rad

    def validate_analyses(self, analyses, options):
        errors = set()
        warnings = set()
        analyses = self._validate_analyses(analyses, options, errors, warnings)

        if errors:
            raise ValidationError(*errors)

        if warnings:
            warning = ValidationWarning(*warnings)
            warnings_module.warn(warning)

        return analyses

    def _validate_analyses(self, analyses, options, errors, warnings):
        outanalyses = []

        for analysis in analyses:
            outanalysis = self._validate_analysis(analysis, options, errors, warnings)
            outanalyses.append(outanalysis)

        return outanalyses

    def validate_analysis(self, analysis, options):
        errors = set()
        warnings = set()
        analysis = self._validate_analysis(analysis, options, errors, warnings)

        if errors:
            raise ValidationError(*errors)

        if warnings:
            warning = ValidationWarning(*warnings)
            warnings_module.warn(warning)

        return analysis

    def _validate_analysis(self, analysis, options, errors, warnings):
        analysis_class = analysis.__class__
        if analysis_class not in self.analysis_validate_methods:
            exc = ValueError('Analysis ({0}) is not supported.'
                             .format(analysis_class.__name__))
            errors.add(exc)
            return analysis

        method = self.analysis_validate_methods[analysis_class]
        return method(analysis, options, errors, warnings)

    def _validate_analysis_photonintensity(self, analysis, options, errors, warnings):
        photon_detector = \
            self._validate_detector_photon(analysis.photon_detector, options, errors, warnings)

        return PhotonIntensityAnalysis(photon_detector)

    def _validate_analysis_kratio(self, analysis, options, errors, warnings):
        photon_detector = \
            self._validate_detector_photon(analysis.photon_detector, options, errors, warnings)
        standard_materials = \
            self._validate_analysis_kratio_standard_materials(analysis.standard_materials, options, errors, warnings)

        return KRatioAnalysis(photon_detector, standard_materials)

    def _validate_analysis_kratio_standard_materials(self, materials, options, errors, warnings):
        outmaterials = {}

        for z, material in materials.items():
            outmaterial = self._validate_material(material, options, errors, warnings)

            if z not in outmaterial.composition:
                exc = ValueError('Standard for element {0} does not have this element in its composition'
                                 .format(pyxray.element_symbol(z)))
                errors.add(exc)
                continue

            outmaterials[z] = outmaterial

        return outmaterials

    def validate_tags(self, tags, options):
        errors = set()
        warnings = set()
        tags = self._validate_tags(tags, options, errors, warnings)

        if errors:
            raise ValidationError(*errors)

        if warnings:
            warning = ValidationWarning(*warnings)
            warnings_module.warn(warning)

        return tags

    def _validate_tags(self, tags, options, errors, warnings):
        outtags = []

        for tag in tags:
            if not isinstance(tag, str):
                exc = TypeError('Tag must be a string')
                errors.add(exc)
                continue
            outtags.append(tag)

        return outtags
