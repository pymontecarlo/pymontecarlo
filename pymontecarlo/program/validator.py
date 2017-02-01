""""""

# Standard library modules.
import math

# Third party modules.
import pyxray.descriptor

# Local modules.
from pymontecarlo.exceptions import ValidationError
from pymontecarlo.options.material import VACUUM
from pymontecarlo.options.sample import \
    Substrate, Inclusion, HorizontalLayers, VerticalLayers, Sphere

# Globals and constants variables.

class Validator(object):

    def __init__(self):
        self.sample_validate_methods = {}
        self.sample_validate_methods[Substrate] = self._validate_sample_substrate
        self.sample_validate_methods[Inclusion] = self._validate_sample_inclusion
        self.sample_validate_methods[HorizontalLayers] = self._validate_sample_horizontallayers
        self.sample_validate_methods[VerticalLayers] = self._validate_sample_verticallayers
        self.sample_validate_methods[Sphere] = self._validate_sample_sphere

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
