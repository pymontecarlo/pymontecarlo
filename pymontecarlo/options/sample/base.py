"""
Base classes for samples.
"""

__all__ = ["LayerBuilder", "Layer"]

# Standard library modules.
import abc
import math
import itertools

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.options.material import VACUUM
from pymontecarlo.util.cbook import unique
from pymontecarlo.util.human import camelcase_to_words
import pymontecarlo.options.base as base

# Globals and constants variables.


class SampleBase(base.OptionBase):
    """
    Base class for all sample representations.
    """

    TILT_TOLERANCE_rad = math.radians(1e-3)  # 0.001 deg
    AZIMUTH_TOLERANCE_rad = math.radians(1e-3)  # 0.001 deg

    def __init__(self, tilt_rad=0.0, azimuth_rad=0.0):
        """
        Creates a new sample.

        :arg tilt_rad: tilt around the x-axis
        :type tilt_rad: :class:`float`

        :arg azimuth_rad: rotation around the z-axis of the tilted sample
        :type azimuth_rad: :class:`float`
        """
        super().__init__()

        self.tilt_rad = tilt_rad
        self.azimuth_rad = azimuth_rad

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and base.isclose(
                self.tilt_rad, other.tilt_rad, abs_tol=self.TILT_TOLERANCE_rad
            )
            and base.isclose(
                self.azimuth_rad, other.azimuth_rad, abs_tol=self.AZIMUTH_TOLERANCE_rad
            )
        )

    def _cleanup_materials(self, *materials):
        materials = list(materials)

        if VACUUM in materials:
            materials.remove(VACUUM)

        return tuple(unique(materials))

    @abc.abstractproperty
    def materials(self):  # pragma: no cover
        """
        Returns a :class:`tuple` of all materials inside this geometry.
        :obj:`VACUUM` should not be included in the materials.
        """
        raise NotImplementedError

    @property
    def atomic_numbers(self):
        """
        Returns a :class:`frozenset` of all atomic numbers inside this geometry.
        """
        zs = set()
        for material in self.materials:
            zs |= set(material.composition.keys())
        return zs

    tilt_deg = base.DegreesAttribute("tilt_rad")
    azimuth_deg = base.DegreesAttribute("azimuth_rad")

    # region HDF5

    ATTR_TILT = "tilt (rad)"
    ATTR_AZIMUTH = "azimuth (rad)"

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_TILT, self.tilt_rad)
        self._convert_hdf5(group, self.ATTR_AZIMUTH, self.azimuth_rad)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_column(
            "sample tilt", "theta0", self.tilt_rad, "rad", self.TILT_TOLERANCE_rad
        )
        builder.add_column(
            "sample azimuth",
            "phi0",
            self.azimuth_rad,
            "rad",
            self.AZIMUTH_TOLERANCE_rad,
        )

    # endregion

    # region Document

    def convert_document(self, builder):
        super().convert_document(builder)

        builder.add_title(camelcase_to_words(self.__class__.__name__))

        section = builder.add_section()
        section.add_title("Orientation")
        description = section.require_description("angles")
        description.add_item(
            "Tilt angle", self.tilt_rad, "rad", self.TILT_TOLERANCE_rad
        )
        description.add_item(
            "Azimuth rotation", self.azimuth_rad, "rad", self.AZIMUTH_TOLERANCE_rad
        )

        section = builder.add_section()
        section.add_title("Material" if len(self.materials) < 2 else "Materials")
        for material in self.materials:
            section.add_entity(material)


# endregion


class SampleBuilderBase(base.OptionBuilderBase):
    def __init__(self):
        self.tilts_rad = set()
        self.azimuths_rad = set()

    def __len__(self):
        tilts_rad = self._calculate_tilt_combinations()
        azimuths_rad = self._calculate_azimuth_combinations()
        return len(tilts_rad) * len(azimuths_rad)

    def _calculate_tilt_combinations(self):
        tilts_rad = self.tilts_rad

        if not tilts_rad:
            tilts_rad = [0.0]

        return tilts_rad

    def _calculate_azimuth_combinations(self):
        azimuths_rad = self.azimuths_rad

        if not azimuths_rad:
            azimuths_rad = [0.0]

        return azimuths_rad

    def add_tilt_rad(self, tilt_rad):
        self.tilts_rad.add(tilt_rad)

    def add_tilt_deg(self, tilt_deg):
        self.add_tilt_rad(math.radians(tilt_deg))

    def add_azimuth_rad(self, azimuth_rad):
        self.azimuths_rad.add(azimuth_rad)

    def add_azimuth_deg(self, azimuth_deg):
        self.add_azimuth_rad(math.radians(azimuth_deg))


class Layer(base.OptionBase):

    THICKNESS_TOLERANCE_m = 1e-12  # 1 fm

    def __init__(self, material, thickness_m):
        """
        Layer of a sample.

        :arg material: material of the layer
        :type material: :class:`Material`

        :arg thickness_m: thickness of the layer in meters
        """
        super().__init__()

        self.material = material
        self.thickness_m = thickness_m

    def __repr__(self):
        return "<{0}(material={1}, thickness={2:g} m)>".format(
            self.__class__.__name__, self.material, self.thickness_m
        )

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and base.isclose(self.material, other.material)
            and base.isclose(
                self.thickness_m, other.thickness_m, abs_tol=self.THICKNESS_TOLERANCE_m
            )
        )

    # region HDF5

    ATTR_MATERIAL = "material"
    ATTR_THICKNESS = "thickness (m)"

    @classmethod
    def parse_hdf5(cls, group):
        material = cls._parse_hdf5(group, cls.ATTR_MATERIAL)
        thickness_m = cls._parse_hdf5(group, cls.ATTR_THICKNESS, float)
        return cls(material, thickness_m)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_MATERIAL, self.material)
        self._convert_hdf5(group, self.ATTR_THICKNESS, self.thickness_m)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_entity(self.material)
        builder.add_column(
            "thickness", "t", self.thickness_m, "m", self.THICKNESS_TOLERANCE_m
        )

    # endregion

    # region Document

    TABLE_LAYER = "layer"

    def convert_document(self, builder):
        super().convert_document(builder)

        table = builder.require_table(self.TABLE_LAYER)

        table.add_column("Material")
        table.add_column("Thickness", "m", self.THICKNESS_TOLERANCE_m)

        row = {"Material": self.material.name, "Thickness": self.thickness_m}
        table.add_row(row)


# endregion


class LayerBuilder(base.OptionBuilderBase):
    def __init__(self):
        self.materials = []
        self.thicknesses_m = set()

    def __len__(self):
        return len(self.materials) * len(self.thicknesses_m)

    def add_material(self, material):
        if material not in self.materials:
            self.materials.append(material)

    def add_thickness_m(self, thickness_m):
        self.thicknesses_m.add(thickness_m)

    def build(self):
        product = itertools.product(self.materials, self.thicknesses_m)

        layers = []
        for material, thickness_m in product:
            layers.append(Layer(material, thickness_m))

        return layers


class LayeredSampleBase(SampleBase):
    def __init__(self, layers=None, tilt_rad=0.0, azimuth_rad=0.0):
        super().__init__(tilt_rad, azimuth_rad)

        if layers is None:
            layers = []
        self.layers = list(layers)

    def __eq__(self, other):
        return super().__eq__(other) and base.are_sequence_equal(
            self.layers, other.layers
        )

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

    # region HDF5

    DATASET_LAYERS = "layers"

    @classmethod
    def _parse_hdf5_layers(cls, group):
        dataset = group[cls.DATASET_LAYERS]
        return [cls._parse_hdf5_reference(group, reference) for reference in dataset]

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5_layers(group, self.layers)

    def _convert_hdf5_layers(self, group, layers):
        shape = (len(layers),)
        ref_dtype = h5py.special_dtype(ref=h5py.Reference)
        dataset = group.create_dataset(
            self.DATASET_LAYERS, shape=shape, dtype=ref_dtype
        )

        for i, layer in enumerate(layers):
            dataset[i] = self._convert_hdf5_reference(group, layer)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)

        for i, layer in enumerate(self.layers):
            prefix = "layer #{0:d} ".format(i)
            prefix_abbrev = "L{0:d} ".format(i)
            builder.add_entity(layer, prefix, prefix_abbrev)

    # endregion

    # region Document

    def convert_document(self, builder):
        super().convert_document(builder)

        section = builder.add_section()
        section.add_title("Layer" if len(self.layers) < 2 else "Layers")
        for layer in self.layers:
            section.add_entity(layer)


# endregion


class LayeredSampleBuilderBase(SampleBuilderBase):
    def __init__(self):
        super().__init__()
        self.layer_builders = []

    def __len__(self):
        layers_list = self._calculate_layer_combinations()
        return super().__len__() * len(layers_list)

    def _calculate_layer_combinations(self):
        layers_list = [builder.build() for builder in self.layer_builders]
        return list(itertools.product(*layers_list))

    def add_layer_builder(self, builder):
        self.layer_builders.append(builder)

    def add_layer(self, material, thickness_m):
        builder = LayerBuilder()
        builder.add_material(material)
        builder.add_thickness_m(thickness_m)
        self.add_layer_builder(builder)
        return builder
