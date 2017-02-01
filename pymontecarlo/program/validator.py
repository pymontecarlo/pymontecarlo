""""""

# Standard library modules.
import math

# Third party modules.
import pyxray.descriptor

# Local modules.
from pymontecarlo.exceptions import ValidationError
from pymontecarlo.options.material import VACUUM
from pymontecarlo.options.particle import PARTICLES
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import \
    (SubstrateSample, InclusionSample, HorizontalLayerSample,
     VerticalLayerSample, SphereSample)
from pymontecarlo.options.limit import ShowersLimit, UncertaintyLimit

# Globals and constants variables.

class Validator(object):

    def __init__(self):
        self.beam_validate_methods = {}
        self.beam_validate_methods[GaussianBeam] = self._validate_beam_gaussian

        self.sample_validate_methods = {}
        self.sample_validate_methods[SubstrateSample] = self._validate_sample_substrate
        self.sample_validate_methods[InclusionSample] = self._validate_sample_inclusion
        self.sample_validate_methods[HorizontalLayerSample] = self._validate_sample_horizontallayers
        self.sample_validate_methods[VerticalLayerSample] = self._validate_sample_verticallayers
        self.sample_validate_methods[SphereSample] = self._validate_sample_sphere

        self.limit_validate_methods = {}
        self.limit_validate_methods[ShowersLimit] = self._validate_limit_showers
        self.limit_validate_methods[UncertaintyLimit] = self._validate_limit_uncertainty

    def validate_material(self, material):
        errors = set()
        self._validate_material(material, errors)

        if errors:
            raise ValidationError(*errors)

    def _validate_material(self, material, errors):
        if material is VACUUM:
            return material

        # Name
        if not material.name.strip():
            exc = ValueError('Name ({0:s}) must be at least one character'
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
            exc = ValueError('Total weight fraction ({0:g}) does not equal 1.0'
                             .format(total))
            errors.add(exc)

        # Density
        if material.density_kg_per_m3 < 0:
            exc = ValueError('Density ({0:g}kg/m3) must be greater or equal to 0'
                             .format(material.density_kg_per_m3))
            errors.add(exc)

    def validate_beam(self, beam):
        errors = set()
        self._validate_beam(beam, errors)

        if errors:
            raise ValidationError(*errors)

    def _validate_beam(self, beam, errors):
        # Energy
        if beam.energy_eV <= 0.0:
            exc = ValueError('Energy ({0:g} eV) must be greater than 0.0'
                             .format(beam.energy_eV))
            errors.add(exc)

        # Particle
        if beam.particle not in PARTICLES:
            exc = ValueError('Unknown particle: {0}'.format(beam.particle))
            errors.add(exc)

        # Specific
        beam_class = beam.__class__
        if beam_class in self.beam_validate_methods:
            method = self.beam_validate_methods[beam_class]
            method(beam, errors)

    def _validate_beam_gaussian(self, beam, errors):
        # Diameter
        if beam.diameter_m < 0.0:
            exc = ValueError('Diameter ({0:g} m) must be greater or equal to 0.0'
                             .format(beam.diameter_m))
            errors.add(exc)

        # x0
        if not math.isfinite(beam.x0_m):
            exc = ValueError('Initial x position must be a finite number')
            errors.add(exc)

        # y0
        if not math.isfinite(beam.y0_m):
            exc = ValueError('Initial y position must be a finite number')
            errors.add(exc)

        # Polar angle
        if not math.isfinite(beam.polar_rad):
            exc = ValueError('Polar angle must be a finite number')
            errors.add(exc)

        # Azimuth angle
        if not math.isfinite(beam.azimuth_rad):
            exc = ValueError('Azimuth angle must be a finite number')
            errors.add(exc)

    def validate_sample(self, sample):
        errors = set()
        self._validate_sample(sample, errors)

        if errors:
            raise ValidationError(*errors)

    def _validate_sample(self, sample, errors):
        # Tilt
        if not math.isfinite(sample.tilt_rad):
            exc = ValueError('Tilt must be a finite number')
            errors.add(exc)

        # Rotation
        if not math.isfinite(sample.rotation_rad):
            exc = ValueError('Rotation must be a finite number')
            errors.add(exc)

        # Sample specific
        sample_class = sample.__class__
        if sample_class in self.sample_validate_methods:
            method = self.sample_validate_methods[sample_class]
            method(sample, errors)

    def _validate_sample_substrate(self, sample, errors):
        if sample.material is VACUUM:
            exc = ValueError('Material cannot be VACUUM')
            errors.add(exc)

        self._validate_material(sample.material, errors)

    def _validate_sample_inclusion(self, sample, errors):
        self._validate_material(sample.substrate_material, errors)

        self._validate_material(sample.inclusion_material, errors)

        if sample.inclusion_diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0'
                             .format(sample.inclusion_diameter_m))
            errors.add(exc)

    def _validate_sample_layer(self, layer, errors):
        self._validate_material(layer.material, errors)

        if layer.thickness_m <= 0:
            exc = ValueError('Thickness ({0:g} m) must be greater than 0'
                             .format(layer.thickness_m))
            errors.add(exc)

    def _validate_sample_horizontallayers(self, sample, errors):
        self._validate_material(sample.substrate_material, errors)

        for layer in sample.layers:
            self._validate_sample_layer(layer, errors)

        if sample.layers and sample.layers[-1].material is VACUUM:
            sample.layers.pop(-1)

    def _validate_sample_verticallayers(self, sample, errors):
        if sample.left_material is VACUUM:
            exc = ValueError('Left material cannot be VACUUM')
            errors.add(exc)

        self._validate_material(sample.left_material, errors)

        if sample.right_material is VACUUM:
            exc = ValueError('Right material cannot be VACUUM')
            errors.add(exc)

        self._validate_material(sample.right_material, errors)

        for layer in sample.layers:
            self._validate_sample_layer(layer, errors)

    def _validate_sample_sphere(self, sample, errors):
        if sample.material is VACUUM:
            exc = ValueError('Material cannot be VACUUM')
            errors.add(exc)

        self._validate_material(sample.material, errors)

        if sample.diameter_m <= 0:
            exc = ValueError('Diameter ({0:g} m) must be greater than 0'
                             .format(sample.diameter_m))
            errors.add(exc)

    def validate_limit(self, limit):
        errors = set()
        self._validate_limit(limit, errors)

        if errors:
            raise ValidationError(*errors)

    def _validate_limit(self, limit, errors):
        # Specific
        limit_class = limit.__class__
        if limit_class in self.limit_validate_methods:
            method = self.limit_validate_methods[limit_class]
            method(limit, errors)

    def _validate_limit_showers(self, limit, errors):
        if limit.showers <= 0:
            exc = ValueError('Number of showers ({0:d}) must be greater than 0'
                             .format(limit.showers))
            errors.add(exc)

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
            exc = ValueError('Uncertainty ({0:g}) must be greater than 0'
                             .format(limit.uncertainty))
            errors.add(exc)

