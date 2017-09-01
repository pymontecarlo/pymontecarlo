""""""

# Standard library modules.
import os
import enum

# Third party modules.

# Local modules.
import pymontecarlo
from pymontecarlo.util.path import get_config_dir
from pymontecarlo.formats.hdf5.reader import HDF5ReaderMixin
from pymontecarlo.formats.hdf5.writer import HDF5WriterMixin

# Globals and constants variables.

class XrayNotation(enum.Enum):
    IUPAC = 'iupac'
    SIEGBAHN = 'siegbahn'

class Settings(HDF5ReaderMixin, HDF5WriterMixin):

    DEFAULT_FILENAME = 'settings.h5'

    def __init__(self):
        # Units
        self.preferred_units = {}

        # X-ray line
        self.preferred_xray_notation = XrayNotation.IUPAC

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

    def set_preferred_unit(self, units):
        if isinstance(units, str):
            units = pymontecarlo.unit_registry.parse_units(units)

        _, base_units = pymontecarlo.unit_registry._get_base_units(units)
        self.preferred_units[base_units] = units

    def clear_preferred_units(self):
        self.preferred_units.clear()

    def to_preferred_unit(self, q, units=None):
        if not hasattr(q, 'units'):
            q = pymontecarlo.unit_registry.Quantity(q, units)

        _, base_unit = pymontecarlo.unit_registry._get_base_units(q.units)

        try:
            preferred_unit = self.preferred_units[base_unit]
            return q.to(preferred_unit)
        except KeyError:
            return q.to(base_unit)
