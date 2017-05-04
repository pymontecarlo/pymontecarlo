"""
Vertical layers sample
"""

# Standard library modules.
import math
import functools
import operator
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.options.sample.base import LayeredSample, LayeredSampleBuilder

# Globals and constants variables.

class VerticalLayerSample(LayeredSample):

    DEPTH_TOLERANCE_m = 1e-12 # 1 fm

    def __init__(self, left_material, right_material, layers=None,
                 depth_m=float('inf'), tilt_rad=0.0, azimuth_rad=0.0):
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
        return '<{0:s}(left_material={1:s}, right_materials={2:s}, {3:d} layers)>' \
            .format(self.__class__.__name__, str(self.left_material),
                    str(self.right_material), len(self.layers))

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.left_material == other.left_material and \
            self.right_material == other.right_material and \
            math.isclose(self.depth_m, other.depth_m, abs_tol=self.DEPTH_TOLERANCE_m)

    @property
    def materials(self):
        return self._cleanup_materials(self.left_material,
                                       self.right_material,
                                       *super().materials)

    @property
    def layers_xpositions_m(self):
        xpositions_m = []

        xmax_m = -sum(layer.thickness_m for layer in self.layers) / 2
        for layer in self.layers:
            xmin_m = xmax_m
            xmax_m = xmin_m + layer.thickness_m
            xpositions_m.append((xmin_m, xmax_m))

        return xpositions_m

class VerticalLayerSampleBuilder(LayeredSampleBuilder):

    def __init__(self):
        super().__init__()
        self.left_materials = []
        self.right_materials = []
        self.depths_m = set()

    def __len__(self):
        it = [super().__len__(),
              self.left_materials,
              self.right_materials,
              self._calculate_depth_m()]
        return functools.reduce(operator.mul, it)

    def _calculate_depth_m(self):
        depths_m = self.depths_m

        if not depths_m:
            depths_m = [float('inf')]

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

        product = itertools.product(left_materials,
                                    right_materials,
                                    layers_list,
                                    depths_m,
                                    tilts_rad,
                                    rotations_rad)
        return [VerticalLayerSample(*args) for args in product]
