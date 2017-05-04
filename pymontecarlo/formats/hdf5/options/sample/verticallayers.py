""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.sample.base import LayeredSampleHDF5Handler
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample

# Globals and constants variables.

class VerticalLayerSampleHDF5Handler(LayeredSampleHDF5Handler):

    ATTR_LEFT_MATERIAL = 'left material'
    ATTR_RIGHT_MATERIAL = 'right material'
    ATTR_DEPTH = 'depth (m)'

    def _parse_left_material(self, group):
        ref_material = group.attrs[self.ATTR_LEFT_MATERIAL]
        return self._parse_material_internal(group, ref_material)

    def _parse_right_material(self, group):
        ref_material = group.attrs[self.ATTR_RIGHT_MATERIAL]
        return self._parse_material_internal(group, ref_material)

    def _parse_depth_m(self, group):
        return float(group.attrs[self.ATTR_DEPTH])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_LEFT_MATERIAL in group.attrs and \
            self.ATTR_RIGHT_MATERIAL in group.attrs and \
            self.ATTR_DEPTH in group.attrs

    def parse(self, group):
        left_material = self._parse_left_material(group)
        right_material = self._parse_right_material(group)
        layers = self._parse_layers(group)
        depth_m = self._parse_depth_m(group)
        tilt_rad = self._parse_tilt_rad(group)
        azimuth_rad = self._parse_azimuth_rad(group)
        return self.CLASS(left_material, right_material, layers, depth_m, tilt_rad, azimuth_rad)

    def _convert_left_material(self, material, group):
        group_material = self._convert_material_internal(material, group)
        group.attrs[self.ATTR_LEFT_MATERIAL] = group_material.ref

    def _convert_right_material(self, material, group):
        group_material = self._convert_material_internal(material, group)
        group.attrs[self.ATTR_RIGHT_MATERIAL] = group_material.ref

    def _convert_depth_m(self, depth_m, group):
        group.attrs[self.ATTR_DEPTH] = depth_m

    def convert(self, sample, group):
        super().convert(sample, group)
        self._convert_left_material(sample.left_material, group)
        self._convert_right_material(sample.right_material, group)
        self._convert_depth_m(sample.depth_m, group)

    @property
    def CLASS(self):
        return VerticalLayerSample
