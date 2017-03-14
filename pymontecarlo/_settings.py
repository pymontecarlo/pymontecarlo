""""""

# Standard library modules.
import os

# Third party modules.

# Local modules.
import pymontecarlo
from pymontecarlo.exceptions import ProgramNotFound
from pymontecarlo.util.entrypoint import resolve_entrypoints
from pymontecarlo.util.path import get_config_dir
from pymontecarlo.fileformat.reader import HDF5ReaderMixin
from pymontecarlo.fileformat.writer import HDF5WriterMixin

# Globals and constants variables.
ENTRYPOINT_AVAILABLE_PROGRAMS = 'pymontecarlo.program'

class Settings(HDF5ReaderMixin, HDF5WriterMixin):

    DEFAULT_FILENAME = 'settings.h5'

    def __init__(self, programs=None):
        # Programs
        if programs is None:
            programs = []
        self.programs = list(programs)

        self._available_programs = None

        # Units
        self.preferred_units = {}

        # X-ray line
        self.preferred_xrayline_notation = 'iupac'
        self.preferred_xrayline_encoding = 'utf16'

    @classmethod
    def read(cls, filepath=None):
        if filepath is None:
            filepath = os.path.join(get_config_dir(), cls.DEFAULT_FILENAME)
        return super().read(filepath)
#
    def write(self, filepath=None):
        if filepath is None:
            filepath = os.path.join(get_config_dir(), self.DEFAULT_FILENAME)
        return super().write(filepath)

    def reload(self):
        self._available_programs = None

    def _load_available_programs(self):
        return resolve_entrypoints(ENTRYPOINT_AVAILABLE_PROGRAMS)

    def iter_available_programs(self):
        # NOTE: The late initialization is required for settings to be loaded
        # correctly in __init__
        if self._available_programs is None:
            self._available_programs = self._load_available_programs()
        return iter(self._available_programs)

    def iter_programs(self):
        """
        Each iteration returns a tuple, where the first item is the class of
        available programs, and the second item is an instance of this program if
        configured, otherwise ``None``.
    
        :arg programs: configured programs
        """
        configured_programs = dict((type(p), p) for p in self.programs)

        for clasz in self.iter_available_programs():
            yield clasz, configured_programs.get(clasz)

    def get_program(self, identifier):
        for program in self.programs:
            if program.getidentifier() == identifier:
                return program
        raise ProgramNotFound('{} is not configured'.format(identifier))

    def set_preferred_unit(self, unit):
        if isinstance(unit, str):
            unit = pymontecarlo.unit_registry.parse_units(unit)

        _, base_unit = pymontecarlo.unit_registry._get_base_units(unit)
        self.preferred_units[base_unit] = unit

    def clear_preferred_units(self):
        self.preferred_units.clear()

    def to_preferred_unit(self, q):
        _, base_unit = pymontecarlo.unit_registry._get_base_units(q.units)

        try:
            preferred_unit = self.preferred_units[base_unit]
            return q.to(preferred_unit)
        except KeyError:
            return q.to(base_unit)
