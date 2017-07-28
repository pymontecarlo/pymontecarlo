""""""

# Standard library modules.

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler
from pymontecarlo.settings import Settings

# Globals and constants variables.

class SettingsHDF5Handler(HDF5Handler):

    GROUP_UNITS = 'units'
    DATASET_PREFERRED_UNITS = 'preferred'
    GROUP_XRAYLINE = 'xrayline'
    ATTR_XRAYLINE_PREFERRED_NOTATION = 'preferred_notation'
    ATTR_XRAYLINE_PREFERRED_ENCODING = 'preferred_encoding'

    def _parse_units(self, obj, group):
        group_units = group[self.GROUP_UNITS]

        for unit in group_units[self.DATASET_PREFERRED_UNITS]:
            obj.set_preferred_unit(unit)

    def _parse_xrayline(self, obj, group):
        group_xrayline = group[self.GROUP_XRAYLINE]
        obj.preferred_xrayline_notation = group_xrayline.attrs[self.ATTR_XRAYLINE_PREFERRED_NOTATION]
        obj.preferred_xrayline_encoding = group_xrayline.attrs[self.ATTR_XRAYLINE_PREFERRED_ENCODING]

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.GROUP_UNITS in group and \
            self.GROUP_XRAYLINE in group

    def parse(self, group):
        obj = Settings()

        self._parse_units(obj, group)
        self._parse_xrayline(obj, group)

        return obj

    def _convert_units(self, obj, group):
        group_units = group.create_group(self.GROUP_UNITS)

        dt = h5py.special_dtype(vlen=str)
        data = list(map(str, obj.preferred_units.values()))
        ds = group_units.create_dataset(self.DATASET_PREFERRED_UNITS, (len(data),), dtype=dt)
        ds[:] = data

    def _convert_xrayline(self, obj, group):
        group_xrayline = group.create_group(self.GROUP_XRAYLINE)
        group_xrayline.attrs[self.ATTR_XRAYLINE_PREFERRED_NOTATION] = obj.preferred_xrayline_notation
        group_xrayline.attrs[self.ATTR_XRAYLINE_PREFERRED_ENCODING] = obj.preferred_xrayline_encoding

    def convert(self, obj, group):
        super().convert(obj, group)
        self._convert_units(obj, group)
        self._convert_xrayline(obj, group)

    @property
    def CLASS(self):
        return Settings
