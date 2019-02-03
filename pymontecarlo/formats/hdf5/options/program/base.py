""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.handler import HDF5HandlerBase
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5HandlerMixin

# Globals and constants variables.

class ProgramHDF5HandlerMixin:

    GROUP_PROGRAMS = 'programs'

    def _parse_program_internal(self, group, ref_program):
        group_program = group.file[ref_program]
        return self._parse_hdf5handlers(group_program)

    def _require_programs_group(self, group):
        return group.file.require_group(self.GROUP_PROGRAMS)

    def _convert_program_internal(self, program, group):
        group_programs = self._require_programs_group(group)

        name = '{} [{:d}]'.format(program.name, id(program))
        if name in group_programs:
            return group_programs[name]

        group_program = group_programs.create_group(name)

        self._convert_hdf5handlers(program, group_program)

        return group_program

class ProgramHDF5HandlerBase(HDF5HandlerBase,
                             ModelHDF5HandlerMixin):
    pass
