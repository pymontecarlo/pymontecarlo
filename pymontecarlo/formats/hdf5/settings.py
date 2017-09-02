""""""

# Standard library modules.

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.formats.hdf5.handler import HDF5Handler
from pymontecarlo.exceptions import ParseError
from pymontecarlo.settings import Settings, XrayNotation

# Globals and constants variables.

class SettingsHDF5Handler(HDF5Handler):

    GROUP_UNITS = 'units'
    DATASET_PREFERRED_UNITS = 'preferred'
    ATTR_PREFERRED_XRAY_NOTATION = 'preferred_xray_notation'

    def _parse_units(self, obj, group):
        group_units = group[self.GROUP_UNITS]
        return list(group_units[self.DATASET_PREFERRED_UNITS])

    def _parse_preferred_xray_notation(self, obj, group):
        name = group.attrs[self.ATTR_PREFERRED_XRAY_NOTATION]
        if name not in XrayNotation.__members__:
            raise ParseError('No notation matching "{}"'.format(name))
        return XrayNotation.__members__[name]

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.GROUP_UNITS in group and \
            self.ATTR_PREFERRED_XRAY_NOTATION in group.attrs

    def parse(self, group):
        obj = Settings()

        for unit in self._parse_units(obj, group):
            obj.set_preferred_unit(unit)
        obj.preferred_xray_notation = self._parse_preferred_xray_notation(obj, group)

        return obj

    def _convert_units(self, obj, group):
        group_units = group.create_group(self.GROUP_UNITS)

        dt = h5py.special_dtype(vlen=str)
        data = list(map(str, obj.preferred_units.values()))
        ds = group_units.create_dataset(self.DATASET_PREFERRED_UNITS, (len(data),), dtype=dt)
        ds[:] = data

    def _convert_preferred_xray_notation(self, notation, group):
        group.attrs[self.ATTR_PREFERRED_XRAY_NOTATION] = notation.name

    def convert(self, obj, group):
        super().convert(obj, group)
        self._convert_units(obj, group)
        self._convert_preferred_xray_notation(obj.preferred_xray_notation, group)

    @property
    def CLASS(self):
        return Settings
