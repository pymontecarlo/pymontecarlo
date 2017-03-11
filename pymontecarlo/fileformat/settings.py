""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.fileformat.base import HDF5Handler
from pymontecarlo import Settings

# Globals and constants variables.

class SettingsHDF5Handler(HDF5Handler):

    CLASS = Settings

    def parse(self, group):
        programs = []

        for subgroup in group.values():
            programs.append(self._parse_hdf5handlers(subgroup))

        return Settings(programs)

    def convert(self, obj, group):
        super().convert(obj, group)

        for program in obj.programs:
            subgroup = group.create_group(program.name)
            self._convert_hdf5handlers(program, subgroup)
