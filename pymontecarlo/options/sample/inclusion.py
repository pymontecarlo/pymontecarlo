"""
Inclusion sample.
"""

# Standard library modules.
import functools
import itertools
import operator
import math

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.base import Sample, SampleBuilder

# Globals and constants variables.

class InclusionSample(Sample):

    INCLUSION_DIAMETER_TOLERANCE_m = 1e-12 # 1 fm

    def __init__(self, substrate_material,
                 inclusion_material, inclusion_diameter_m,
                 tilt_rad=0.0, azimuth_rad=0.0):
        """
        Creates an inclusion sample.
        The sample consists of a hemisphere inclusion inside a substrate.
        """
        super().__init__(tilt_rad, azimuth_rad)

        self.substrate_material = substrate_material
        self.inclusion_material = inclusion_material
        self.inclusion_diameter_m = inclusion_diameter_m

    def __repr__(self):
        return '<{0:s}(substrate_material={1:s}, inclusion_material={2:s}, inclusion_diameter={3:g} m)>' \
            .format(self.__class__.__name__, str(self.substrate_material),
                    str(self.inclusion_material), self.inclusion_diameter_m)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.substrate_material == other.substrate_material and \
            self.inclusion_material == other.inclusion_material and \
            math.isclose(self.inclusion_diameter_m, other.inclusion_diameter_m, abs_tol=self.INCLUSION_DIAMETER_TOLERANCE_m)

    @property
    def materials(self):
        return self._cleanup_materials(self.substrate_material,
                                       self.inclusion_material)

class InclusionSampleBuilder(SampleBuilder):

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
        tilts_rad = self._calculate_tilt_combinations()
        rotations_rad = self._calculate_azimuth_combinations()
        product = itertools.product(self.substrate_materials,
                                    self.inclusion_materials,
                                    self.inclusion_diameters_m,
                                    tilts_rad,
                                    rotations_rad)
        return [InclusionSample(*args) for args in product]
