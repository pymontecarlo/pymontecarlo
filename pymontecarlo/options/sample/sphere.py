"""
Sphere sample.
"""

__all__ = ["SphereSample", "SphereSampleBuilder"]

# Standard library modules.
import functools
import itertools
import operator

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.base import SampleBase, SampleBuilderBase
import pymontecarlo.options.base as base

# Globals and constants variables.


class SphereSample(SampleBase):

    DIAMETER_TOLERANCE_m = 1e-12  # 1 fm

    def __init__(self, material, diameter_m, tilt_rad=0.0, azimuth_rad=0.0):
        """
        Creates a geometry consisting of a sphere.
        The sphere is entirely located below the ``z=0`` plane.

        :arg material: material
        :arg diameter_m: diameter (in meters)
        """
        super().__init__(tilt_rad, azimuth_rad)
        self.material = material
        self.diameter_m = diameter_m

    def __repr__(self):
        return "<{0:s}(material={1:s}, diameter={2:g} m)>".format(
            self.__class__.__name__, str(self.material), self.diameter_m
        )

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and base.isclose(self.material, other.material)
            and base.isclose(
                self.diameter_m, other.diameter_m, abs_tol=self.DIAMETER_TOLERANCE_m
            )
        )

    @property
    def materials(self):
        return self._cleanup_materials(self.material)

    # region HDF5

    ATTR_MATERIAL = "material"
    ATTR_DIAMETER = "diameter (m)"

    @classmethod
    def parse_hdf5(cls, group):
        material = cls._parse_hdf5(group, cls.ATTR_MATERIAL)
        diameter_m = cls._parse_hdf5(group, cls.ATTR_DIAMETER, float)
        tilt_rad = cls._parse_hdf5(group, cls.ATTR_TILT, float)
        azimuth_rad = cls._parse_hdf5(group, cls.ATTR_AZIMUTH, float)
        return cls(material, diameter_m, tilt_rad, azimuth_rad)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_MATERIAL, self.material)
        self._convert_hdf5(group, self.ATTR_DIAMETER, self.diameter_m)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_entity(self.material, "sphere ", "sphere ")
        builder.add_column(
            "sphere diameter", "d", self.diameter_m, "m", self.DIAMETER_TOLERANCE_m
        )

    # endregion

    # region Document

    DESCRIPTION_SPHERE = "sphere"

    def convert_document(self, builder):
        super().convert_document(builder)

        section = builder.add_section()
        section.add_title("Sphere")

        description = section.require_description(self.DESCRIPTION_SPHERE)
        description.add_item("Material", self.material.name)
        description.add_item(
            "Diameter", self.diameter_m, "m", self.DIAMETER_TOLERANCE_m
        )


# endregion


class SphereSampleBuilder(SampleBuilderBase):
    def __init__(self):
        super().__init__()
        self.materials = []
        self.diameters_m = set()

    def __len__(self):
        it = [super().__len__(), len(self.materials), len(self.diameters_m)]
        return functools.reduce(operator.mul, it)

    def add_material(self, material):
        if material not in self.materials:
            self.materials.append(material)

    def add_diameter_m(self, diameter_m):
        self.diameters_m.add(diameter_m)

    def build(self):
        tilts_rad = self._calculate_tilt_combinations()
        rotations_rad = self._calculate_azimuth_combinations()
        product = itertools.product(
            self.materials, self.diameters_m, tilts_rad, rotations_rad
        )
        return [SphereSample(*args) for args in product]
