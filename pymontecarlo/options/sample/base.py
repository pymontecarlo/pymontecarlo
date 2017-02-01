"""
Base classes for samples.
"""

# Standard library modules.
import abc
import math

# Third party modules.
import more_itertools

# Local modules.
from pymontecarlo.options.material import VACUUM
from pymontecarlo.util.cbook import MultiplierAttribute, Builder

# Globals and constants variables.

class _Sample(metaclass=abc.ABCMeta):
    """
    Base class for all sample representations.
    """

    def __init__(self, tilt_rad=0.0, rotation_rad=0.0):
        """
        Creates a new sample.
        
        :arg tilt_rad: tilt around the x-axis
        :type tilt_rad: :class:`float`
        
        :arg rotation_rad: rotation around the z-axis of the tilted sample
        :type rotation_rad: :class:`float`
        """
        self.tilt_rad = tilt_rad
        self.rotation_rad = rotation_rad

    def __eq__(self, other):
        return self.tilt_rad == other.tilt_rad and \
            self.rotation_rad == other.rotation_rad

    def _cleanup_materials(self, *materials):
        materials = list(materials)

        if VACUUM in materials:
            materials.remove(VACUUM)

        return tuple(more_itertools.unique_everseen(materials))

    @abc.abstractproperty
    def materials(self):
        """
        Returns a :class:`tuple` of all materials inside this geometry.
        :obj:`VACUUM` should not be included in the materials.
        """
        raise NotImplementedError

    tilt_deg = MultiplierAttribute('tilt_rad', 180.0 / math.pi)
    rotation_deg = MultiplierAttribute('rotation_rad', 180.0 / math.pi)

class _SampleBuilder(Builder):

    def __init__(self):
        self.tilts_rad = set()
        self.rotations_rad = set()

    def __len__(self):
        tilts_rad, rotations_rad = self._get_combinations()
        return len(tilts_rad) * len(rotations_rad)

    def _get_combinations(self):
        tilts_rad = self.tilts_rad
        rotations_rad = self.rotations_rad

        if not tilts_rad:
            tilts_rad = [0.0]
        if not rotations_rad:
            rotations_rad = [0.0]

        return tilts_rad, rotations_rad

    def add_tilt_rad(self, tilt_rad):
        self.tilts_rad.add(tilt_rad)

    def add_tilt_deg(self, tilt_deg):
        self.add_tilt_deg(math.radians(tilt_deg))

    def add_rotation_rad(self, rotation_rad):
        self.rotations_rad.add(rotation_rad)

    def add_rotation_deg(self, rotation_deg):
        self.add_rotation_rad(math.radians(rotation_deg))

class Layer(object):

    def __init__(self, material, thickness_m):
        """
        Layer of a sample.

        :arg material: material of the layer
        :type material: :class:`Material`

        :arg thickness_m: thickness of the layer in meters
        """
        self.material = material
        self.thickness_m = thickness_m

    def __repr__(self):
        return '<{0:s}(material={1:s}, thickness={2:g} m)>' \
            .format(self.__class__.__name__, self.material, self.thickness_m)

    def __eq__(self, other):
        return self.material == other.material and \
            self.thickness_m == other.thickness_m

class _LayeredSample(_Sample):

    def __init__(self, layers=None, tilt_rad=0.0, rotation_rad=0.0):
        super().__init__(tilt_rad, rotation_rad)

        if layers is None:
            layers = []
        self.layers = list(layers)

    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        if len(self.layers) != len(other.layers):
            return False

        for layer0, layer1 in zip(self.layers, other.layers):
            if layer0 != layer1:
                return False

        return True

    def add_layer(self, material, thickness_m):
        """
        Adds a layer to the geometry.
        The layer is added after the previous layers.

        :arg material: material of the layer
        :type material: :class:`Material`

        :arg thickness: thickness of the layer in meters
        """
        layer = Layer(material, thickness_m)
        self.layers.append(layer)
        return layer

    @property
    def materials(self):
        materials = [layer.material for layer in self.layers]
        return self._cleanup_materials(*materials)
