"""
Substrate sample.
"""

__all__ = ["SubstrateSample", "SubstrateSampleBuilder"]

# Standard library modules.
import functools
import itertools
import operator

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.base import SampleBase, SampleBuilderBase
import pymontecarlo.options.base as base

# Globals and constants variables.


class SubstrateSample(SampleBase):
    def __init__(self, material, tilt_rad=0.0, azimuth_rad=0.0):
        """
        Creates a substrate sample. 
        At tilt of 0.0\u00b0, the sample is entirely made of the specified 
        material below ``z = 0``.
        """
        super().__init__(tilt_rad, azimuth_rad)
        self.material = material

    def __repr__(self):
        return "<{0:s}(material={1:s})>".format(
            self.__class__.__name__, str(self.material)
        )

    def __eq__(self, other):
        return super().__eq__(other) and base.isclose(self.material, other.material)

    @property
    def materials(self):
        return self._cleanup_materials(self.material)

    # region HDF5

    ATTR_MATERIAL = "material"

    @classmethod
    def parse_hdf5(cls, group):
        material = cls._parse_hdf5(group, cls.ATTR_MATERIAL)
        tilt_rad = cls._parse_hdf5(group, cls.ATTR_TILT, float)
        azimuth_rad = cls._parse_hdf5(group, cls.ATTR_AZIMUTH, float)
        return cls(material, tilt_rad, azimuth_rad)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_MATERIAL, self.material)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_entity(self.material, "substrate ", "subs ")

    # endregion

    # region Document

    def convert_document(self, builder):
        super().convert_document(builder)


# endregion


class SubstrateSampleBuilder(SampleBuilderBase):
    def __init__(self):
        super().__init__()
        self.materials = []

    def __len__(self):
        it = [super().__len__(), len(self.materials)]
        return functools.reduce(operator.mul, it)

    def add_material(self, material):
        if material not in self.materials:
            self.materials.append(material)

    def build(self):
        tilts_rad = self._calculate_tilt_combinations()
        rotations_rad = self._calculate_azimuth_combinations()
        product = itertools.product(self.materials, tilts_rad, rotations_rad)
        return [SubstrateSample(*args) for args in product]
