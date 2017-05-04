""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.sample.base import LayeredSampleHDF5Handler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample

# Globals and constants variables.

class HorizontalLayerSampleHDF5Handler(LayeredSampleHDF5Handler):

    ATTR_SUBSTRATE = 'substrate'

    def _parse_substrate_material(self, group):
        ref_material = group.attrs[self.ATTR_SUBSTRATE]
        return self._parse_material_internal(group, ref_material)

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_SUBSTRATE in group.attrs

    def parse(self, group):
        substrate_material = self._parse_substrate_material(group)
        layers = self._parse_layers(group)
        tilt_rad = self._parse_tilt_rad(group)
        azimuth_rad = self._parse_azimuth_rad(group)
        return self.CLASS(substrate_material, layers, tilt_rad, azimuth_rad)

    def _convert_substrate_material(self, material, group):
        group_material = self._convert_material_internal(material, group)
        group.attrs[self.ATTR_SUBSTRATE] = group_material.ref

    def convert(self, sample, group):
        super().convert(sample, group)
        self._convert_substrate_material(sample.substrate_material, group)

    @property
    def CLASS(self):
        return HorizontalLayerSample
