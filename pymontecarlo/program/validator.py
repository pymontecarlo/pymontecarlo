"""
Base validation.
"""

# Standard library modules.
import math

# Third party modules.
import pyxray.descriptor

# Local modules.
from pymontecarlo.exceptions import ValidationError
from pymontecarlo.options.material import VACUUM
from pymontecarlo.options.particle import PARTICLES
from pymontecarlo.options.detector import PhotonDetector

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
        self.detector_validate_methods = {}
        self.limit_validate_methods = {}
        self.model_validate_methods = {}
        self.analysis_validate_methods = {}

        self.valid_models = {}
        self.default_models = {}

    def validate_options(self, options):
        errors = set()
        options = self._validate_options(options, errors)

        if errors:
            raise ValidationError(*errors)

        return options

    def _validate_options(self, options, errors):
        options.beam = \
            self._validate_beam(options.beam, options, errors)
        options.sample = \
            self._validate_sample(options.sample, options, errors)
        options.detectors = \
            self._validate_detectors(options.detectors, options, errors)
        options.limits = \
            self._validate_limits(options.limits, options, errors)
        options.models = \
            self._validate_models(options.models, options, errors)
        options.analyses = \
            self._validate_analyses(options.analyses, options, errors)

        return options

    def validate_beam(self, beam, options):
        errors = set()
        beam = self._validate_beam(beam, options, errors)

        if errors:
            raise ValidationError(*errors)

        return beam

    def _validate_beam(self, beam, options, errors):
        beam.energy_eV = \
            self._validate_beam_base_energy_eV(beam.energy_eV, options, errors)
        beam.particle = \
            self._validate_beam_base_particle(beam.particle, options, errors)

        # Specific
        beam_class = beam.__class__
        if beam_class not in self.beam_validate_methods:
            exc = ValueError('Beam ({0}) is not supported.'
                             .format(beam_class.__name__))
            errors.add(exc)
            return beam

        method = self.beam_validate_methods[beam_class]
        beam = method(beam, options, errors)

        return beam

    def _validate_beam_base_energy_eV(self, energy_eV, options, errors):
        if energy_eV <= 0.0:
            exc = ValueError('Energy ({0:g} eV) must be greater than 0.0.'
                             .format(energy_eV))
            errors.add(exc)

        return energy_eV

    def _validate_beam_base_particle(self, particle, options, errors):
        if particle not in PARTICLES:
            exc = ValueError('Unknown particle: {0}.'.format(particle))
            errors.add(exc)

        return particle

    def _validate_beam_gaussian(self, beam, options, errors):
        beam.diameter_m = \
            self._validate_beam_gaussian_diameter_m(beam.diameter_m, options, errors)
        beam.x0_m = \
            self._validate_beam_gaussian_x0_m(beam.x0_m, options, errors)
        beam.y0_m = \
            self._validate_beam_gaussian_y0_m(beam.y0_m, options, errors)
        beam.polar_rad = \
            self._validate_beam_gaussian_polar_rad(beam.polar_rad, options, errors)
        beam.azimuth_rad = \
            self._validate_beam_gaussian_azimuth_rad(beam.azimuth_rad, options, errors)

        return beam

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

    def _validate_beam_gaussian_polar_rad(self, polar_rad, options, errors):
        if not math.isfinite(polar_rad):
            exc = ValueError('Polar angle must be a finite number.')
            errors.add(exc)

        return polar_rad

    def _validate_beam_gaussian_azimuth_rad(self, azimuth_rad, options, errors):
        if not math.isfinite(azimuth_rad):
            exc = ValueError('Azimuth angle must be a finite number.')
            errors.add(exc)

        return azimuth_rad

    def validate_material(self, material, options):
        errors = set()
        material = self._validate_material(material, options, errors)

        if errors:
            raise ValidationError(*errors)

        return material

    def _validate_material(self, material, options, errors):
        if material is VACUUM:
            return material

        material.name = \
            self._validate_material_base_name(material.name, options, errors)
        material.composition = \
            self._validate_material_base_composition(material.composition, options, errors)
        material.density_kg_per_m3 = \
            self._validate_material_base_density_kg_per_m3(material.density_kg_per_m3, options, errors)

        return material

    def _validate_material_base_name(self, name, options, errors):
        name = name.strip()
        if not name:
            exc = ValueError('Name ({0:s}) must be at least one character.'
                             .format(name))
            errors.add(exc)

        return name

    def _validate_material_base_composition(self, composition, options, errors):
        for z in composition:
            try:
                pyxray.descriptor.Element.validate(z)
            except ValueError as exc:
                errors.add(exc)

        total = sum(composition.values())
        if total != 1.0:
            exc = ValueError('Total weight fraction ({0:g}) does not equal 1.0.'
                             .format(total))
            errors.add(exc)

        return composition

    def _validate_material_base_density_kg_per_m3(self, density_kg_per_m3, options, errors):
        if density_kg_per_m3 < 0:
            exc = ValueError('Density ({0:g}kg/m3) must be greater or equal to 0.'
                             .format(density_kg_per_m3))
            errors.add(exc)

        return density_kg_per_m3

    def validate_sample(self, sample, options):
        errors = set()
        self._validate_sample(sample, options, errors)

        if errors:
            raise ValidationError(*errors)

        return sample

    def _validate_sample(self, sample, options, errors):
        sample.tilt_rad = \
            self._validate_sample_base_tilt_rad(sample.tilt_rad, options, errors)
        sample.rotation_rad = \
            self._validate_sample_base_rotation_rad(sample.rotation_rad, options, errors)

        # Sample specific
        sample_class = sample.__class__
        if sample_class not in self.sample_validate_methods:
            exc = ValueError('Sample ({0}) is not supported.'
                             .format(sample_class.__name__))
            errors.add(exc)
            return sample

        method = self.sample_validate_methods[sample_class]
        sample = method(sample, options, errors)

        return sample

    def _validate_sample_base_tilt_rad(self, tilt_rad, options, errors):
        if not math.isfinite(tilt_rad):
            exc = ValueError('Tilt must be a finite number.')
            errors.add(exc)

        return tilt_rad

    def _validate_sample_base_rotation_rad(self, rotation_rad, options, errors):
        if not math.isfinite(rotation_rad):
            exc = ValueError('Rotation must be a finite number.')
            errors.add(exc)

        return rotation_rad

    def _validate_sample_substrate(self, sample, options, errors):
        sample.material = \
            self._validate_sample_substrate_material(sample.material, options, errors)

        return sample

    def _validate_sample_substrate_material(self, material, options, errors):
        if material is VACUUM:
            exc = ValueError('Material cannot be VACUUM.')
            errors.add(exc)

        return self._validate_material(material, options, errors)

    def _validate_sample_inclusion(self, sample, options, errors):
        sample.substrate_material = \
            self._validate_sample_inclusion_substrate_material(sample.substrate_material, options, errors)
        sample.inclusion_material = \
            self._validate_sample_inclusion_inclusion_material(sample.inclusion_material, options, errors)
        sample.inclusion_diameter_m = \
            self._validate_sample_inclusion_inclusion_diameter_m(sample.inclusion_diameter_m, options, errors)

        return sample

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
        layer.material = self._validate_material(layer.material, options, errors)

        if layer.thickness_m <= 0:
            exc = ValueError('Thickness ({0:g} m) must be greater than 0.'
                             .format(layer.thickness_m))
            errors.add(exc)

        return layer

    def _validate_sample_layered_layers(self, layers, options, errors):
        for i, layer in enumerate(layers):
            layers[i] = self._validate_sample_layered_layer(layer, options, errors)

        return layers

    def _validate_sample_horizontallayers(self, sample, options, errors):
        sample.substrate_material = \
            self._validate_sample_horizontallayers_substrate_material(sample.substrate_material, options, errors)
        sample.layers = \
            self._validate_sample_horizontallayers_layers(sample.layers, options, errors)

        return sample

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
        sample.left_material = \
            self._validate_sample_verticallayers_left_material(sample.left_material, options, errors)
        sample.right_material = \
            self._validate_sample_verticallayers_left_material(sample.right_material, options, errors)
        sample.layers = \
            self._validate_sample_verticallayers_layers(sample.layers, options, errors)
        sample.depth_m = \
            self._validate_sample_verticallayers_depth_m(sample.depth_m, options, errors)

        return sample

    def _validate_sample_verticallayers_left_material(self, material, options, errors):
        if material is VACUUM:
            exc = ValueError('Left material cannot be VACUUM.')
            errors.add(exc)

        material = self._validate_material(material, options, errors)

        return material

    def _validate_sample_verticallayers_right_material(self, material, options, errors):
        if material is VACUUM:
            exc = ValueError('Right material cannot be VACUUM.')
            errors.add(exc)

        material = self._validate_material(material, options, errors)

        return material

    def _validate_sample_verticallayers_layers(self, layers, options, errors):
        return self._validate_sample_layered_layers(layers, options, errors)

    def _validate_sample_verticallayers_depth_m(self, depth_m, options, errors):
        if depth_m <= 0.0:
            exc = ValueError('Depth ({0:g} m) must be greater than 0.'
                             .format(depth_m))
            errors.add(exc)

        return depth_m

    def _validate_sample_sphere(self, sample, options, errors):
        sample.material = \
            self._validate_sample_sphere_material(sample.material, options, errors)
        sample.diameter_m = \
            self._validate_sample_sphere_diameter_m(sample.diameter_m, options, errors)

        return sample

    def _validate_sample_sphere_material(self, material, options, errors):
        if material is VACUUM:
            exc = ValueError('Material cannot be VACUUM.')
            errors.add(exc)

        material = self._validate_material(material, options, errors)

        return material

    def _validate_sample_sphere_diameter_m(self, diameter_m, options, errors):
        if diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0.'
                             .format(diameter_m))
            errors.add(exc)

        return diameter_m

    def validate_detectors(self, detectors, options):
        errors = set()
        detectors = self._validate_detectors(detectors, options, errors)

        if errors:
            raise ValidationError(*errors)

        return detectors

    def _validate_detectors(self, detectors, options, errors):
        for i, detector in enumerate(detectors):
            detectors[i] = self._validate_detector(detector, options, errors)

        return detectors

    def validate_detector(self, detector, options):
        errors = set()
        detector = self._validate_detector(detector, options, errors)

        if errors:
            raise ValidationError(*errors)

        return detector

    def _validate_detector(self, detector, options, errors):
        detector_class = detector.__class__
        if detector_class not in self.detector_validate_methods:
            exc = ValueError('Detector ({0}) is not supported.'
                             .format(detector_class.__name__))
            errors.add(exc)
            return detector

        method = self.detector_validate_methods[detector_class]
        detector = method(detector, options, errors)

        return detector

    def _validate_detector_photon(self, detector, options, errors):
        detector.elevation_rad = \
            self._validate_detector_photon_elevation_rad(detector.elevation_rad, options, errors)
        detector.azimuth_rad = \
            self._validate_detector_photon_azimuth_rad(detector.azimuth_rad, options, errors)

        return detector

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
            exc = ValueError('At least one limit must be defined')
            errors.add(exc)

        for i, limit in enumerate(limits):
            limits[i] = self._validate_limit(limit, options, errors)

        return limits

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
        limit = method(limit, options, errors)

        return limit

    def _validate_limit_showers(self, limit, options, errors):
        limit.showers = \
            self._validate_limit_showers_showers(limit.showers, options, errors)

        return limit

    def _validate_limit_showers_showers(self, showers, options, errors):
        if showers <= 0:
            exc = ValueError('Number of showers ({0:d}) must be greater than 0.'
                             .format(showers))
            errors.add(exc)

        return showers

    def _validate_limit_uncertainty(self, limit, options, errors):
        limit.atomic_number = \
            self._validate_limit_uncertainty_atomic_number(limit.atomic_number, options, errors)
        limit.transition = \
            self._validate_limit_uncertainty_transition(limit.transition, options, errors)
        limit.detector = \
            self._validate_limit_uncertainty_detector(limit.detector, options, errors)
        limit.uncertainty = \
            self._validate_limit_uncertainty_uncertainty(limit.uncertainty, options, errors)

        return limit

    def _validate_limit_uncertainty_atomic_number(self, atomic_number, options, errors):
        try:
            pyxray.descriptor.Element.validate(atomic_number)
        except ValueError as exc:
            errors.add(exc)

        return atomic_number

    def _validate_limit_uncertainty_transition(self, transition, options, errors):
        #TODO: Validate uncertainty limit transition
        return transition

    def _validate_limit_uncertainty_detector(self, detector, options, errors):
        #TODO: Validate uncertainty limit detector
        return detector

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
        for i, model in enumerate(models):
            models[i] = self._validate_model(model, options, errors)

        # Add default model if missing
        model_classes = set()
        for model in models:
            model_classes.add(model.__class__)

        for model_class, default_model in self.default_models.items():
            if model_class not in model_classes:
                models.append(default_model)

        return models

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
        model = method(model, options, errors)

        return model

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
        for i, analysis in enumerate(analyses):
            analyses[i] = self._validate_analysis(analysis, options, errors)

        return analyses

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
        analysis = method(analysis, options, errors)

        return analysis

    def _validate_analysis_photonintensity(self, analysis, options, errors):
        if not options.find_detectors(PhotonDetector):
            exc = ValueError('Analysis ({0}) requires a photon detector'
                             .format(analysis))
            errors.add(exc)

        return analysis

    def _validate_analysis_kratio(self, analysis, options, errors):
        self._validate_analysis_photonintensity(analysis, options, errors)

        analysis.standard_materials = \
            self._validate_analysis_kratio_standard_materials(analysis.standard_materials, options, errors)

        return analysis

    def _validate_analysis_kratio_standard_materials(self, materials, options, errors):
        for z, material in materials.items():
            materials[z] = self._validate_material(material, options, errors)

            if z not in material.composition:
                exc = ValueError('Standard for element {0} does not have this element in its composition'
                                 .format(pyxray.element_symbol(z)))
                errors.add(exc)

        return materials

