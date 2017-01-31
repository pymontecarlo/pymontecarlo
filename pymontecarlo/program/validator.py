""""""

# Standard library modules.

# Third party modules.
import pyxray.descriptor

# Local modules.
from pymontecarlo.exceptions import ValidationError

# Globals and constants variables.

class Validator(object):

    def validate_material(self, material):
        errors = set()
        material = self._validate_material(material, errors)

        if errors:
            raise ValidationError(*errors)

        return material

    def _validate_material(self, material, errors):
        material.name = \
            self._validate_material_name(material.name, errors)
        material.composition = \
            self._validate_material_composition(material.composition, errors)
        material.density_kg_per_m3 = \
            self._validate_material_density_kg_per_m3(material.density_kg_per_m3, errors)
        return material

    def _validate_material_name(self, name, errors):
        name = name.strip()

        if not name:
            exc = ValueError('Name ({0:s}) must be at least one character'
                             .format(name))
            errors.add(exc)

        return name

    def _validate_material_composition(self, composition, errors):
        for z in composition:
            try:
                pyxray.descriptor.Element.validate(z)
            except ValueError as exc:
                errors.add(exc)

        total = sum(composition.values())
        if total != 1.0:
            exc = ValueError('Total weight fraction ({0:g}) does not equal 1.0'
                             .format(total))
            errors.add(exc)

        return composition

    def _validate_material_density_kg_per_m3(self, density_kg_per_m3, errors):
        if density_kg_per_m3 < 0:
            exc = ValueError('Density ({0:g}kg/m3) must be greater or equal to 0'
                             .format(density_kg_per_m3))
            errors.add(exc)

        return density_kg_per_m3

