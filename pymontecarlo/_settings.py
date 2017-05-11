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

    activated_programs_changed = Signal()
    preferred_units_changed = Signal()
    preferred_xrayline_notation_changed = Signal()
    preferred_xrayline_encoding_changed = Signal()

    def __init__(self):
        # Programs
        self._activated_programs = {} # key: identifier, value: program object
        self._available_programs = {} # key: identifier, value: program class

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
        for program in self.activated_programs:
            validator = program.create_validator()
            validator._validate_program(program, None, errors)

    def validate(self):
        errors = set()
        self._validate(errors)

        if errors:
            raise ValidationError(*errors)

    def update(self, settings):
        settings.validate()

        self._activated_programs.clear()
        self._activated_programs = settings._activated_programs.copy()

        self.preferred_units.clear()
        self.preferred_units.update(settings.preferred_units)
        self.preferred_units_changed.send()

        self.preferred_xrayline_notation = settings.preferred_xrayline_notation
        self.preferred_xrayline_encoding = settings.preferred_xrayline_encoding

    def reload(self):
        self._available_programs.clear()
        entrypoint._ENTRYPOINTS.clear()

    def get_activated_program(self, identifier):
        """
        Returns the :class:`Program` matching the specified identifier.
        """
        try:
            return self._activated_programs[identifier]
        except KeyError:
            raise ProgramNotFound('{} is not configured'.format(identifier))

    def get_available_program_class(self, identifier):
        """
        Returns the :class:`Program` class matching the specified identifier.
        """
        try:
            self.available_programs # Initialize
            return self._available_programs[identifier]
        except KeyError:
            raise ProgramNotFound('{} is not available'.format(identifier))

    def is_program_activated(self, identifier):
        return identifier in self._activated_programs

    def is_program_available(self, identifier):
        return identifier in self._available_programs

    def activate_program(self, program):
        identifier = program.getidentifier()

        if self.is_program_activated(identifier):
            raise ValueError('{} is already activated'.format(identifier))

        self._activated_programs[identifier] = program
        self.activated_programs_changed.send()

    def deactivate_program(self, identifier):
        self._activated_programs.pop(identifier, None)
        self.activated_programs_changed.send()

    def deactivate_all_programs(self):
        self._activated_programs.clear()
        self.activated_programs_changed.send()

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
    def activated_programs(self):
        """
        Returns a :class:`tuple` of all activated programs. 
        The items are :class:`Program` instances.
        """
        return tuple(self._activated_programs.values())

    @property
    def available_programs(self):
        """
        Returns a :class:`tuple` of all available programs, whether or not
        they are activated.
        The items are :class:`Program` classes.
        """
        # Late initialization
        if not self._available_programs:
            self._available_programs = {}

            for clasz in entrypoint.resolve_entrypoints(ENTRYPOINT_AVAILABLE_PROGRAMS):
                identifier = clasz.getidentifier()
                self._available_programs[identifier] = clasz

        return tuple(self._available_programs.values())

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
