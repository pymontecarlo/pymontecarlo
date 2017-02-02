""""""

# Standard library modules.
import math

# Third party modules.
import pyxray.descriptor

# Local modules.
from pymontecarlo.exceptions import ValidationError
from pymontecarlo.options.material import VACUUM
from pymontecarlo.options.particle import PARTICLES

# Globals and constants variables.

class Validator(object):

    def __init__(self):
        self.beam_validate_methods = {}
        self.sample_validate_methods = {}
        self.limit_validate_methods = {}

    def validate_material(self, material):
        errors = set()
        material = self._validate_material(material, errors)

        if errors:
            raise ValidationError(*errors)

        return material

    def _validate_material(self, material, errors):
        if material is VACUUM:
            return material

        # Name
        material.name = material.name.strip()
        if not material.name:
            exc = ValueError('Name ({0:s}) must be at least one character.'
                             .format(material.name))
            errors.add(exc)

        # Composition
        for z in material.composition:
            try:
                pyxray.descriptor.Element.validate(z)
            except ValueError as exc:
                errors.add(exc)

        total = sum(material.composition.values())
        if total != 1.0:
            exc = ValueError('Total weight fraction ({0:g}) does not equal 1.0.'
                             .format(total))
            errors.add(exc)

        # Density
        if material.density_kg_per_m3 < 0:
            exc = ValueError('Density ({0:g}kg/m3) must be greater or equal to 0.'
                             .format(material.density_kg_per_m3))
            errors.add(exc)

        return material

    def validate_beam(self, beam):
        errors = set()
        beam = self._validate_beam(beam, errors)

        if errors:
            raise ValidationError(*errors)

        return beam

    def _validate_beam(self, beam, errors):
        # Energy
        if beam.energy_eV <= 0.0:
            exc = ValueError('Energy ({0:g} eV) must be greater than 0.0.'
                             .format(beam.energy_eV))
            errors.add(exc)

        # Particle
        if beam.particle not in PARTICLES:
            exc = ValueError('Unknown particle: {0}.'.format(beam.particle))
            errors.add(exc)

        # Specific
        beam_class = beam.__class__
        if beam_class not in self.beam_validate_methods:
            exc = ValueError('Beam ({0}) is not supported.'
                             .format(beam_class.__name__))
            errors.add(exc)
        else:
            method = self.beam_validate_methods[beam_class]
            beam = method(beam, errors)

        return beam

    def _validate_beam_gaussian(self, beam, errors):
        # Diameter
        if beam.diameter_m < 0.0:
            exc = ValueError('Diameter ({0:g} m) must be greater or equal to 0.0.'
                             .format(beam.diameter_m))
            errors.add(exc)

        # x0
        if not math.isfinite(beam.x0_m):
            exc = ValueError('Initial x position must be a finite number.')
            errors.add(exc)

        # y0
        if not math.isfinite(beam.y0_m):
            exc = ValueError('Initial y position must be a finite number.')
            errors.add(exc)

        # Polar angle
        if not math.isfinite(beam.polar_rad):
            exc = ValueError('Polar angle must be a finite number.')
            errors.add(exc)

        # Azimuth angle
        if not math.isfinite(beam.azimuth_rad):
            exc = ValueError('Azimuth angle must be a finite number.')
            errors.add(exc)

        return beam

    def validate_sample(self, sample):
        errors = set()
        self._validate_sample(sample, errors)

        if errors:
            raise ValidationError(*errors)

        return sample

    def _validate_sample(self, sample, errors):
        # Tilt
        if not math.isfinite(sample.tilt_rad):
            exc = ValueError('Tilt must be a finite number.')
            errors.add(exc)

        # Rotation
        if not math.isfinite(sample.rotation_rad):
            exc = ValueError('Rotation must be a finite number.')
            errors.add(exc)

        # Sample specific
        sample_class = sample.__class__
        if sample_class not in self.sample_validate_methods:
            exc = ValueError('Sample ({0}) is not supported.'
                             .format(sample_class.__name__))
            errors.add(exc)
        else:
            method = self.sample_validate_methods[sample_class]
            sample = method(sample, errors)

        return sample

    def _validate_sample_substrate(self, sample, errors):
        if sample.material is VACUUM:
            exc = ValueError('Material cannot be VACUUM.')
            errors.add(exc)

        sample.material = self._validate_material(sample.material, errors)

        return sample

    def _validate_sample_inclusion(self, sample, errors):
        sample.substrate_material = \
            self._validate_material(sample.substrate_material, errors)

        sample.inclusion_material = \
            self._validate_material(sample.inclusion_material, errors)

        if sample.inclusion_diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0.'
                             .format(sample.inclusion_diameter_m))
            errors.add(exc)

        return sample

    def _validate_sample_layer(self, layer, errors):
        layer.material = self._validate_material(layer.material, errors)

        if layer.thickness_m <= 0:
            exc = ValueError('Thickness ({0:g} m) must be greater than 0.'
                             .format(layer.thickness_m))
            errors.add(exc)

        return layer

    def _validate_sample_layered(self, sample, errors):
        for i, layer in enumerate(sample.layers):
            sample.layers[i] = self._validate_sample_layer(layer, errors)

        return sample

    def _validate_sample_horizontallayers(self, sample, errors):
        sample.substrate_material = \
            self._validate_material(sample.substrate_material, errors)

        sample = self._validate_sample_layered(sample, errors)

        if sample.layers and sample.layers[-1].material is VACUUM:
            sample.layers.pop(-1)

        if not sample.layers:
            exc = ValueError('At least one layer must be defined.')
            errors.add(ValueError(exc))

        return sample

    def _validate_sample_verticallayers(self, sample, errors):
        if sample.left_material is VACUUM:
            exc = ValueError('Left material cannot be VACUUM.')
            errors.add(exc)

        sample.left_material = \
            self._validate_material(sample.left_material, errors)

        if sample.right_material is VACUUM:
            exc = ValueError('Right material cannot be VACUUM.')
            errors.add(exc)

        sample.right_material = \
            self._validate_material(sample.right_material, errors)

        sample = self._validate_sample_layered(sample, errors)

        if sample.depth_m <= 0.0:
            exc = ValueError('Depth ({0:g} m) must be greater than 0.'
                             .format(sample.depth_m))
            errors.add(exc)

        return sample

    def _validate_sample_sphere(self, sample, errors):
        if sample.material is VACUUM:
            exc = ValueError('Material cannot be VACUUM.')
            errors.add(exc)

        sample.material = self._validate_material(sample.material, errors)

        if sample.diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0.'
                             .format(sample.diameter_m))
            errors.add(exc)

        return sample

    def validate_limit(self, limit):
        errors = set()
        limit = self._validate_limit(limit, errors)

        if errors:
            raise ValidationError(*errors)

        return limit

    def _validate_limit(self, limit, errors):
        # Specific
        limit_class = limit.__class__
        if limit_class not in self.limit_validate_methods:
            exc = ValueError('Limit ({0}) is not supported.'
                             .format(limit_class.__name__))
            errors.add(exc)
        else:
            method = self.limit_validate_methods[limit_class]
            limit = method(limit, errors)

        return limit

    def _validate_limit_showers(self, limit, errors):
        if limit.showers <= 0:
            exc = ValueError('Number of showers ({0:d}) must be greater than 0.'
                             .format(limit.showers))
            errors.add(exc)

        return limit

    def _validate_limit_uncertainty(self, limit, errors):
        # Atomic number
        try:
            pyxray.descriptor.Element.validate(limit.atomic_number)
        except ValueError as exc:
            errors.add(exc)

        # Transition
        #TODO: Validate transition

        # Detector
        #TODO: Validate detector

        # Uncertainty
        if limit.uncertainty <= 0:
            exc = ValueError('Uncertainty ({0:g}) must be greater than 0.'
                             .format(limit.uncertainty))
            errors.add(exc)

        return limit

