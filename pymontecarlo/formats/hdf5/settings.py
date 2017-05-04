""""""

# Standard library modules.

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler
from pymontecarlo import Settings

# Globals and constants variables.

class SettingsHDF5Handler(HDF5Handler):

    def _parse_programs(self, obj, group):
        if 'programs' not in group:
            return

        group_programs = group['programs']
        for group_program in group_programs.values():
            obj.programs.append(self._parse_hdf5handlers(group_program))

    def _parse_units(self, obj, group):
        if 'units' not in group:
            return

        group_units = group['units']

        if 'preferred' not in group_units:
            return

        for unit in group_units['preferred']:
            obj.set_preferred_unit(unit)

    def _parse_xrayline(self, obj, group):
        if 'xrayline' not in group:
            return

        group_xrayline = group['xrayline']

        if 'preferred_notation' in group_xrayline.attrs:
            obj.preferred_xrayline_notation = group_xrayline.attrs['preferred_notation']

        if 'preferred_encoding' in group_xrayline.attrs:
            obj.preferred_xrayline_encoding = group_xrayline.attrs['preferred_encoding']

    def parse(self, group):
        obj = Settings()

        self._parse_programs(obj, group)
        self._parse_units(obj, group)
        self._parse_xrayline(obj, group)

        return obj

    def _convert_programs(self, programs, group):
        group_programs = group.create_group('programs')

        for program in programs:
            group_program = group_programs.create_group(program.getidentifier())
            self._convert_hdf5handlers(program, group_program)

    def _convert_units(self, obj, group):
        group_units = group.create_group('units')

        dt = h5py.special_dtype(vlen=str)
        data = list(map(str, obj.preferred_units.values()))
        ds = group_units.create_dataset("preferred", (len(data),), dtype=dt)
        ds[:] = data

    def _convert_xrayline(self, obj, group):
        group_xrayline = group.create_group('xrayline')
        group_xrayline.attrs['preferred_notation'] = obj.preferred_xrayline_notation
        group_xrayline.attrs['preferred_encoding'] = obj.preferred_xrayline_encoding

    def convert(self, obj, group):
        super().convert(obj, group)
        self._convert_programs(obj.programs, group)
        self._convert_units(obj, group)
        self._convert_xrayline(obj, group)

    @property
    def CLASS(self):
        return Settings
