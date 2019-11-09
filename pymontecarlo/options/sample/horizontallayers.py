"""
Horizontal layers sample.
"""

__all__ = ["HorizontalLayerSample", "HorizontalLayerSampleBuilder"]

# Standard library modules.
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.base import LayeredSampleBase, LayeredSampleBuilderBase
from pymontecarlo.options.material import VACUUM
import pymontecarlo.options.base as base

# Globals and constants variables.


class HorizontalLayerSample(LayeredSampleBase):
    def __init__(
        self, substrate_material=None, layers=None, tilt_rad=0.0, azimuth_rad=0.0
    ):
        """
        Creates a multi-layers geometry.
        The layers are assumed to be in the x-y plane (normal parallel to z) at
        tilt of 0.0\u00b0.
        The first layer starts at ``z = 0`` and extends towards the negative z
        axis.

        :arg substrate_material: material of the substrate.
            If ``None``, the geometry does not have a substrate, only layers
        :arg layers: :class:`list` of :class:`.Layer`
        """
        super().__init__(layers, tilt_rad, azimuth_rad)

        if substrate_material is None:
            substrate_material = VACUUM
        self.substrate_material = substrate_material

    def __repr__(self):
        if self.has_substrate():
            return "<{0:s}(substrate_material={1:s}, {2:d} layers)>".format(
                self.__class__.__name__, str(self.substrate_material), len(self.layers)
            )
        else:
            return "<{0:s}(No substrate, {1:d} layers)>".format(
                self.__class__.__name__, len(self.layers)
            )

    def __eq__(self, other):
        return super().__eq__(other) and base.isclose(
            self.substrate_material, other.substrate_material
        )

    def has_substrate(self):
        """
        Returns ``True`` if a substrate material has been defined.
        """
        return self.substrate_material is not VACUUM

    @property
    def materials(self):
        return self._cleanup_materials(self.substrate_material, *super().materials)

    @property
    def layers_zpositions_m(self):
        zpositions = []

        zmin_m = 0.0
        for layer in self.layers:
            zmax_m = zmin_m
            zmin_m = zmax_m - layer.thickness_m
            zpositions.append((zmin_m, zmax_m))

        return zpositions

    # region HDF5

    ATTR_SUBSTRATE = "substrate"

    @classmethod
    def parse_hdf5(cls, group):
        substrate_material = cls._parse_hdf5(group, cls.ATTR_SUBSTRATE)
        layers = cls._parse_hdf5_layers(group)
        tilt_rad = cls._parse_hdf5(group, cls.ATTR_TILT, float)
        azimuth_rad = cls._parse_hdf5(group, cls.ATTR_AZIMUTH, float)
        return cls(substrate_material, layers, tilt_rad, azimuth_rad)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_SUBSTRATE, self.substrate_material)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_entity(self.substrate_material, "substrate ", "subs ")

    # endregion

    # region Document

    DESCRIPTION_SUBSTRATE = "substrate"

    def convert_document(self, builder):
        super().convert_document(builder)

        section = builder.add_section()
        section.add_title("Substrate")

        description = section.require_description(self.DESCRIPTION_SUBSTRATE)
        description.add_item("Material", self.substrate_material.name)


# endregion


class HorizontalLayerSampleBuilder(LayeredSampleBuilderBase):
    def __init__(self):
        super().__init__()
        self.substrate_materials = []

    def __len__(self):
        substrate_materials = self._calculate_subtrate_material_combinations()
        return super().__len__() * len(substrate_materials)

    def _calculate_subtrate_material_combinations(self):
        substrate_materials = self.substrate_materials

        if not substrate_materials:
            substrate_materials = [None]

        return substrate_materials

    def add_substrate_material(self, material):
        if material not in self.substrate_materials:
            self.substrate_materials.append(material)

    def build(self):
        substrate_materials = self._calculate_subtrate_material_combinations()
        layers_list = self._calculate_layer_combinations()
        tilts_rad = self._calculate_tilt_combinations()
        rotations_rad = self._calculate_azimuth_combinations()

        product = itertools.product(
            substrate_materials, layers_list, tilts_rad, rotations_rad
        )
        return [HorizontalLayerSample(*args) for args in product]
