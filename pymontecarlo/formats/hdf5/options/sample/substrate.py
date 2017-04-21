""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.sample.base import SampleHDF5Handler
from pymontecarlo.options.sample.substrate import SubstrateSample

# Globals and constants variables.

class SubstrateSampleHDF5Handler(SampleHDF5Handler):

    ATTR_MATERIAL = 'material'

    def _parse_material(self, group):
        ref_material = group.attrs[self.ATTR_MATERIAL]
        return self._parse_material_internal(group, ref_material)

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_MATERIAL in group.attrs

    def parse(self, group):
        material = self._parse_material(group)
        tilt_rad = self._parse_tilt_rad(group)
        azimuth_rad = self._parse_azimuth_rad(group)
        return self.CLASS(material, tilt_rad, azimuth_rad)

    def _convert_material(self, material, group):
        group_material = self._convert_material_internal(material, group)
        group.attrs[self.ATTR_MATERIAL] = group_material.ref

    def convert(self, sample, group):
        super().convert(sample, group)
        self._convert_material(sample.material, group)

    @property
    def CLASS(self):
        return SubstrateSample
