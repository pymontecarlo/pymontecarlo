"""
Inclusion sample.
"""

# Standard library modules.
import functools
import itertools
import operator

# Third party modules.

# Local modules.
from .base import _Sample, _SampleBuilder

# Globals and constants variables.

class Inclusion(_Sample):

    def __init__(self, substrate_material,
                 inclusion_material, inclusion_diameter_m,
                 tilt_rad=0.0, rotation_rad=0.0):
        """
        Creates an inclusion sample.
        The sample consists of a hemisphere inclusion inside a substrate.
        """
        super().__init__(tilt_rad, rotation_rad)

        self.substrate_material = substrate_material
        self.inclusion_material = inclusion_material
        self.inclusion_diameter_m = inclusion_diameter_m

    def __repr__(self):
        return '<{0:s}(substrate_material={1:s}, inclusion_material={2:s}, inclusion_diameter={3:g} m)>' \
            .format(self.__class__.__name__, self.substrate.material,
                    self.inclusion.material, self.inclusion.diameter_m)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.substrate_material == other.substrate_material and \
            self.inclusion_material == other.inclusion_material and \
            self.inclusion_diameter_m == other.inclusion_diameter_m

    @property
    def materials(self):
        return self._cleanup_materials(self.substrate_material,
                                       self.inclusion_material)

class InclusionBuilder(_SampleBuilder):

    def __init__(self):
        super().__init__()
        self.substrate_materials = []
        self.inclusion_materials = []
        self.inclusion_diameters_m = set()

    def __len__(self):
        it = [super().__len__(),
              len(self.substrate_materials), len(self.inclusion_materials),
              len(self.inclusion_diameters_m)]
        return functools.reduce(operator.mul, it)

    def add_substrate_material(self, material):
        if material not in self.substrate_materials:
            self.substrate_materials.append(material)

    def add_inclusion_material(self, material):
        if material not in self.inclusion_materials:
            self.inclusion_materials.append(material)

    def add_inclusion_diameter_m(self, diameter_m):
        self.inclusion_diameters_m.add(diameter_m)

    def build(self):
        product = itertools.product(self.substrate_materials,
                                    self.inclusion_materials,
                                    self.inclusion_diameters_m,
                                    *self._get_combinations())
        return [Inclusion(*args) for args in product]