""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.sample.base import SampleHDF5Handler
from pymontecarlo.options.sample.inclusion import InclusionSample

# Globals and constants variables.

class InclusionSampleHDF5Handler(SampleHDF5Handler):

    ATTR_SUBSTRATE = 'substrate'
    ATTR_INCLUSION = 'inclusion'
    ATTR_DIAMETER = 'diameter (m)'

    def _parse_substrate_material(self, group):
        ref_material = group.attrs[self.ATTR_SUBSTRATE]
        return self._parse_material_internal(group, ref_material)

    def _parse_inclusion_material(self, group):
        ref_material = group.attrs[self.ATTR_INCLUSION]
        return self._parse_material_internal(group, ref_material)

    def _parse_diameter_m(self, group):
        return float(group.attrs[self.ATTR_DIAMETER])

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_SUBSTRATE in group.attrs and \
            self.ATTR_INCLUSION in group.attrs and \
            self.ATTR_DIAMETER in group.attrs

    def parse(self, group):
        substrate_material = self._parse_substrate_material(group)
        inclusion_material = self._parse_inclusion_material(group)
        diameter_m = self._parse_diameter_m(group)
        tilt_rad = self._parse_tilt_rad(group)
        azimuth_rad = self._parse_azimuth_rad(group)
        return self.CLASS(substrate_material, inclusion_material, diameter_m, tilt_rad, azimuth_rad)

    def _convert_substrate_material(self, material, group):
        group_material = self._convert_material_internal(material, group)
        group.attrs[self.ATTR_SUBSTRATE] = group_material.ref

    def _convert_inclusion_material(self, material, group):
        group_material = self._convert_material_internal(material, group)
        group.attrs[self.ATTR_INCLUSION] = group_material.ref

    def _convert_diameter_m(self, diameter_m, group):
        group.attrs[self.ATTR_DIAMETER] = diameter_m

    def convert(self, sample, group):
        super().convert(sample, group)
        self._convert_substrate_material(sample.substrate_material, group)
        self._convert_inclusion_material(sample.inclusion_material, group)
        self._convert_diameter_m(sample.inclusion_diameter_m, group)

    @property
    def CLASS(self):
        return InclusionSample
