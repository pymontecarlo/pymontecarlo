"""
Vertical layers sample
"""

__all__ = ["VerticalLayerSample", "VerticalLayerSampleBuilder"]

# Standard library modules.
import functools
import operator
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.base import LayeredSampleBase, LayeredSampleBuilderBase
import pymontecarlo.options.base as base

# Globals and constants variables.


class VerticalLayerSample(LayeredSampleBase):

    DEPTH_TOLERANCE_m = 1e-12  # 1 fm

    def __init__(
        self,
        left_material,
        right_material,
        layers=None,
        depth_m=float("inf"),
        tilt_rad=0.0,
        azimuth_rad=0.0,
    ):
        """
        Creates a grain boundaries sample.
        It consists of 0 or many layers in the y-z plane (normal parallel to x)
        simulating interfaces between different materials.
        If no layer is defined, the geometry is a couple.

        :arg left_material: material on the left side
        :arg right_material: material on the right side
        :arg layers: :class:`list` of :class:`.Layer`
        """
        super().__init__(layers, tilt_rad, azimuth_rad)

        self.left_material = left_material
        self.right_material = right_material

        self.depth_m = depth_m

    def __repr__(self):
        return "<{0:s}(left_material={1:s}, right_materials={2:s}, {3:d} layers)>".format(
            self.__class__.__name__,
            str(self.left_material),
            str(self.right_material),
            len(self.layers),
        )

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and base.isclose(self.left_material, other.left_material)
            and base.isclose(self.right_material, other.right_material)
            and base.isclose(
                self.depth_m, other.depth_m, abs_tol=self.DEPTH_TOLERANCE_m
            )
        )

    @property
    def materials(self):
        return self._cleanup_materials(
            self.left_material, self.right_material, *super().materials
        )

    @property
    def layers_xpositions_m(self):
        xpositions_m = []

        xmax_m = -sum(layer.thickness_m for layer in self.layers) / 2
        for layer in self.layers:
            xmin_m = xmax_m
            xmax_m = xmin_m + layer.thickness_m
            xpositions_m.append((xmin_m, xmax_m))

        return xpositions_m

    # region HDF5

    ATTR_LEFT_MATERIAL = "left material"
    ATTR_RIGHT_MATERIAL = "right material"
    ATTR_DEPTH = "depth (m)"

    @classmethod
    def parse_hdf5(cls, group):
        left_material = cls._parse_hdf5(group, cls.ATTR_LEFT_MATERIAL)
        right_material = cls._parse_hdf5(group, cls.ATTR_RIGHT_MATERIAL)
        layers = cls._parse_hdf5_layers(group)
        depth_m = cls._parse_hdf5(group, cls.ATTR_DEPTH, float)
        tilt_rad = cls._parse_hdf5(group, cls.ATTR_TILT, float)
        azimuth_rad = cls._parse_hdf5(group, cls.ATTR_AZIMUTH, float)
        return cls(
            left_material, right_material, layers, depth_m, tilt_rad, azimuth_rad
        )

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_LEFT_MATERIAL, self.left_material)
        self._convert_hdf5(group, self.ATTR_RIGHT_MATERIAL, self.right_material)
        self._convert_hdf5(group, self.ATTR_DEPTH, self.depth_m)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_entity(self.left_material, "left substrate ", "left ")
        builder.add_entity(self.right_material, "right substrate ", "right ")
        builder.add_column(
            "vertical layers depth", "zmax", self.depth_m, "m", self.DEPTH_TOLERANCE_m
        )

    # endregion

    # region Document

    DESCRIPTION_VERTICAL_LAYER = "vertical layer"

    def convert_document(self, builder):
        super().convert_document(builder)

        section = builder.add_section()
        section.add_title("Substrates")

        description = section.require_description(self.DESCRIPTION_VERTICAL_LAYER)
        description.add_item("Left material", self.left_material.name)
        description.add_item("Right material", self.right_material.name)
        description.add_item("Depth", self.depth_m, "m", self.DEPTH_TOLERANCE_m)


# endregion


class VerticalLayerSampleBuilder(LayeredSampleBuilderBase):
    def __init__(self):
        super().__init__()
        self.left_materials = []
        self.right_materials = []
        self.depths_m = set()

    def __len__(self):
        it = [
            super().__len__(),
            len(self.left_materials),
            len(self.right_materials),
            len(self._calculate_depth_m()),
        ]
        return functools.reduce(operator.mul, it)

    def _calculate_depth_m(self):
        depths_m = self.depths_m

        if not depths_m:
            depths_m = [float("inf")]

        return depths_m

    def add_left_material(self, material):
        if material not in self.left_materials:
            self.left_materials.append(material)

    def add_right_material(self, material):
        if material not in self.right_materials:
            self.right_materials.append(material)

    def add_depth_m(self, depth_m):
        self.depths_m.add(depth_m)

    def build(self):
        left_materials = self.left_materials
        right_materials = self.right_materials
        layers_list = self._calculate_layer_combinations()
        depths_m = self._calculate_depth_m()
        tilts_rad = self._calculate_tilt_combinations()
        rotations_rad = self._calculate_azimuth_combinations()

        product = itertools.product(
            left_materials,
            right_materials,
            layers_list,
            depths_m,
            tilts_rad,
            rotations_rad,
        )
        return [VerticalLayerSample(*args) for args in product]
