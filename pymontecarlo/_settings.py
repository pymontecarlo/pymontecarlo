""""""

# Standard library modules.
import os

# Third party modules.

# Local modules.
import pymontecarlo
from pymontecarlo.exceptions import ProgramNotFound, ValidationError
import pymontecarlo.util.entrypoint as entrypoint
from pymontecarlo.util.path import get_config_dir
from pymontecarlo.formats.hdf5.reader import HDF5ReaderMixin
from pymontecarlo.formats.hdf5.writer import HDF5WriterMixin
from pymontecarlo.util.signal import Signal

# Globals and constants variables.
ENTRYPOINT_AVAILABLE_PROGRAMS = 'pymontecarlo.program'

class Settings(HDF5ReaderMixin, HDF5WriterMixin):

    DEFAULT_FILENAME = 'settings.h5'

    preferred_units_changed = Signal()
    preferred_xrayline_notation_changed = Signal()
    preferred_xrayline_encoding_changed = Signal()

    def __init__(self, programs=None):
        # Programs
        if programs is None:
            programs = []
        self.programs = list(programs)

        self._available_programs = None

        # Units
        self.preferred_units = {}

        # X-ray line
        self._preferred_xrayline_notation = 'iupac'
        self._preferred_xrayline_encoding = 'utf16'

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

    def _validate(self, errors):
        # Programs
        for program in self.programs:
            validator = program.create_validator()
            validator._validate_program(program, None, errors)

    def validate(self):
        errors = set()
        self._validate(errors)

        if errors:
            raise ValidationError(*errors)

    def update(self, settings):
        settings.validate()

        self.programs.clear()
        self.programs = settings.programs.copy()

        self.preferred_units.clear()
        self.preferred_units.update(settings.preferred_units)
        self.preferred_units_changed.send()

        self.preferred_xrayline_notation = settings.preferred_xrayline_notation
        self.preferred_xrayline_encoding = settings.preferred_xrayline_encoding

    def reload(self):
        self._available_programs = None
        entrypoint._ENTRYPOINTS.clear()

    def iter_available_programs(self):
        # NOTE: The late initialization is required for settings to be loaded
        # correctly in __init__
        if self._available_programs is None:
            self._available_programs = \
                entrypoint.resolve_entrypoints(ENTRYPOINT_AVAILABLE_PROGRAMS)
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
        """
        Returns the :class:`Program` matching the specified identifier.
        """
        for program in self.programs:
            if program.getidentifier() == identifier:
                return program
        raise ProgramNotFound('{} is not configured'.format(identifier))

    def has_program(self, identifier):
        for program in self.programs:
            if program.getidentifier() == identifier:
                return True
        return False

    def set_preferred_unit(self, units, quiet=False):
        if isinstance(units, str):
            units = pymontecarlo.unit_registry.parse_units(units)

        _, base_units = pymontecarlo.unit_registry._get_base_units(units)
        self.preferred_units[base_units] = units

        if not quiet:
            self.preferred_units_changed.send()

    def clear_preferred_units(self, quiet=False):
        self.preferred_units.clear()

        if not quiet:
            self.preferred_units_changed.send()

    def to_preferred_unit(self, q, units=None):
        if not hasattr(q, 'units'):
            q = pymontecarlo.unit_registry.Quantity(q, units)

        _, base_unit = pymontecarlo.unit_registry._get_base_units(q.units)

        try:
            preferred_unit = self.preferred_units[base_unit]
            return q.to(preferred_unit)
        except KeyError:
            return q.to(base_unit)

    @property
    def preferred_xrayline_notation(self):
        return self._preferred_xrayline_notation

    @preferred_xrayline_notation.setter
    def preferred_xrayline_notation(self, notation):
        if self._preferred_xrayline_notation == notation:
            return
        self._preferred_xrayline_notation = notation
        self.preferred_xrayline_notation_changed.send()

    @property
    def preferred_xrayline_encoding(self):
        return self._preferred_xrayline_encoding

    @preferred_xrayline_encoding.setter
    def preferred_xrayline_encoding(self, encoding):
        if self._preferred_xrayline_encoding == encoding:
            return
        self._preferred_xrayline_encoding = encoding
        self.preferred_xrayline_encoding_changed.send()
