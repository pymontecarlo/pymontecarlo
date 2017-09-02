""""""

# Standard library modules.

# Third party modules.
import h5py

import numpy as np

# Local modules.
from pymontecarlo.formats.hdf5.handler import HDF5Handler
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

        name = program.name
        if name in group_programs:
            return group_programs[name]

        group_program = group_programs.create_group(name)

        self._convert_hdf5handlers(program, group_program)

        return group_program

class ProgramHDF5Handler(HDF5Handler,
                         ModelHDF5HandlerMixin):

    ATTR_NAME = 'name'

    def _parse_name(self, group):
        return group.attrs[self.ATTR_NAME]

    def parse(self, group):
        program = super().parse(group)
        program.name = self._parse_name(group)
        return program

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_NAME in group.attrs

    def _convert_name(self, name, group):
        group.attrs[self.ATTR_NAME] = name

    def convert(self, program, group):
        super().convert(program, group)
        self._convert_name(program.name, group)
