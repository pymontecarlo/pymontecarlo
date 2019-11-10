"""
Inclusion sample.
"""

__all__ = ["InclusionSample", "InclusionSampleBuilder"]

# Standard library modules.
import functools
import itertools
import operator

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.base import SampleBase, SampleBuilderBase
import pymontecarlo.options.base as base

# Globals and constants variables.


class InclusionSample(SampleBase):

    INCLUSION_DIAMETER_TOLERANCE_m = 1e-12  # 1 fm

    def __init__(
        self,
        substrate_material,
        inclusion_material,
        inclusion_diameter_m,
        tilt_rad=0.0,
        azimuth_rad=0.0,
    ):
        """
        Creates an inclusion sample.
        The sample consists of a hemisphere inclusion inside a substrate.
        """
        super().__init__(tilt_rad, azimuth_rad)

        self.substrate_material = substrate_material
        self.inclusion_material = inclusion_material
        self.inclusion_diameter_m = inclusion_diameter_m

    def __repr__(self):
        return "<{0:s}(substrate_material={1:s}, inclusion_material={2:s}, inclusion_diameter={3:g} m)>".format(
            self.__class__.__name__,
            str(self.substrate_material),
            str(self.inclusion_material),
            self.inclusion_diameter_m,
        )

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and base.isclose(self.substrate_material, other.substrate_material)
            and base.isclose(self.inclusion_material, other.inclusion_material)
            and base.isclose(
                self.inclusion_diameter_m,
                other.inclusion_diameter_m,
                abs_tol=self.INCLUSION_DIAMETER_TOLERANCE_m,
            )
        )

    @property
    def materials(self):
        return self._cleanup_materials(self.substrate_material, self.inclusion_material)

    # region HDF5

    ATTR_SUBSTRATE = "substrate"
    ATTR_INCLUSION = "inclusion"
    ATTR_DIAMETER = "diameter (m)"

    @classmethod
    def parse_hdf5(cls, group):
        substrate_material = cls._parse_hdf5(group, cls.ATTR_SUBSTRATE)
        inclusion_material = cls._parse_hdf5(group, cls.ATTR_INCLUSION)
        inclusion_diameter_m = cls._parse_hdf5(group, cls.ATTR_DIAMETER, float)
        tilt_rad = cls._parse_hdf5(group, cls.ATTR_TILT, float)
        azimuth_rad = cls._parse_hdf5(group, cls.ATTR_AZIMUTH, float)
        return cls(
            substrate_material,
            inclusion_material,
            inclusion_diameter_m,
            tilt_rad,
            azimuth_rad,
        )

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_SUBSTRATE, self.substrate_material)
        self._convert_hdf5(group, self.ATTR_INCLUSION, self.inclusion_material)
        self._convert_hdf5(group, self.ATTR_DIAMETER, self.inclusion_diameter_m)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_entity(self.substrate_material, "substrate ", "subs ")
        builder.add_entity(self.inclusion_material, "inclusion ", "incl ")
        builder.add_column(
            "inclusion diameter",
            "d",
            self.inclusion_diameter_m,
            "m",
            self.INCLUSION_DIAMETER_TOLERANCE_m,
        )

    # endregion

    # region Document

    DESCRIPTION_SUBTRATE = "substrate"
    DESCRIPTION_INCLUSION = "inclusion"

    def convert_document(self, builder):
        super().convert_document(builder)

        section = builder.add_section()
        section.add_title("Substrate")

        description = section.require_description(self.DESCRIPTION_SUBTRATE)
        description.add_item("Material", self.substrate_material.name)

        section = builder.add_section()
        section.add_title("Inclusion")

        description = section.require_description(self.DESCRIPTION_INCLUSION)
        description.add_item("Material", self.inclusion_material.name)
        description.add_item(
            "Diameter",
            self.inclusion_diameter_m,
            "m",
            self.INCLUSION_DIAMETER_TOLERANCE_m,
        )


# endregion


class InclusionSampleBuilder(SampleBuilderBase):
    def __init__(self):
        super().__init__()
        self.substrate_materials = []
        self.inclusion_materials = []
        self.inclusion_diameters_m = set()

    def __len__(self):
        it = [
            super().__len__(),
            len(self.substrate_materials),
            len(self.inclusion_materials),
            len(self.inclusion_diameters_m),
        ]
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
        product = itertools.product(
            self.substrate_materials,
            self.inclusion_materials,
            self.inclusion_diameters_m,
            tilts_rad,
            rotations_rad,
        )
        return [InclusionSample(*args) for args in product]
