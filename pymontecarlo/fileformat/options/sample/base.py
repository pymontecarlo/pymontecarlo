""""""

# Standard library modules.
import abc

# Third party modules.
import numpy as np

import h5py

# Local modules.
from pymontecarlo.fileformat.base import HDF5Handler
from pymontecarlo.fileformat.options.material import MaterialHDF5HandlerMixin
from pymontecarlo.options.sample.base import Layer

# Globals and constants variables.

class SampleHDF5Handler(HDF5Handler, MaterialHDF5HandlerMixin):

    ATTR_TILT = 'tilt_rad'
    ATTR_ROTATION = 'rotation_rad'

    def _parse_tilt_rad(self, group):
        return float(group.attrs[self.ATTR_TILT])

    def _parse_rotation_rad(self, group):
        return float(group.attrs[self.ATTR_ROTATION])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_TILT in group.attrs and \
            self.ATTR_ROTATION in group.attrs

    def _convert_tilt_rad(self, sample, group):
        group.attrs[self.ATTR_TILT] = sample.tilt_rad

    def _convert_rotation_rad(self, sample, group):
        group.attrs[self.ATTR_ROTATION] = sample.rotation_rad

    @abc.abstractmethod
    def convert(self, sample, group):
        super().convert(sample, group)
        self._convert_tilt_rad(sample, group)
        self._convert_rotation_rad(sample, group)

class LayerHDF5Handler(HDF5Handler, MaterialHDF5HandlerMixin):

    ATTR_MATERIAL = 'material'
    ATTR_THICKNESS = 'thickness_m'

    def _parse_material(self, group):
        ref_material = group.attrs[self.ATTR_MATERIAL]
        return self._parse_material_internal(group, ref_material)

    def _parse_thickness_m(self, group):
        return float(group.attrs[self.ATTR_THICKNESS])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_MATERIAL in group.attrs and \
            self.ATTR_THICKNESS in group.attrs

    def parse(self, group):
        material = self._parse_material(group)
        thickness_m = self._parse_thickness_m(group)
        return self.CLASS(material, thickness_m)

    def _convert_material(self, material, group):
        group_material = self._convert_material_internal(material, group)
        group.attrs[self.ATTR_MATERIAL] = group_material.ref

    def _convert_thickness_m(self, thickness_m, group):
        group.attrs[self.ATTR_THICKNESS] = thickness_m

    def convert(self, layer, group):
        super().convert(layer, group)
        self._convert_material(layer.material, group)
        self._convert_thickness_m(layer.thickness_m, group)

    @property
    def CLASS(self):
        return Layer

class LayeredSampleHDF5Handler(SampleHDF5Handler, MaterialHDF5HandlerMixin):

    GROUP_LAYERS = 'layers'
    ATTR_LAYERS = 'layers'

    def _parse_layer_internal(self, group, ref_layer):
        group_layer = group.file[ref_layer]
        return self._parse_hdf5handlers(group_layer)

    def _parse_layers(self, group):
        layers = []

        for ref_layer in group.attrs[self.ATTR_LAYERS]:
            layer = self._parse_layer_internal(group, ref_layer)
            layers.append(layer)

        return layers

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_LAYERS in group.attrs

    def _convert_layer_internal(self, layer, group):
        group.require_group(self.GROUP_MATERIALS)
        group_layers = group.require_group(self.GROUP_LAYERS)

        name = str(id(layer))
        if name in group_layers:
            return group_layers[name]

        group_layer = group_layers.create_group(name)

        self._convert_hdf5handlers(layer, group_layer)

        return group_layer

    def _convert_layers(self, layers, group):
        refs = []

        for layer in layers:
            group_layer = self._convert_layer_internal(layer, group)
            refs.append(group_layer.ref)

        dtype = h5py.special_dtype(ref=h5py.Reference)
        group.attrs.create(self.ATTR_LAYERS, np.array(refs), dtype=dtype)

    @abc.abstractmethod
    def convert(self, sample, group):
        super().convert(sample, group)
        self._convert_layers(sample.layers, group)

