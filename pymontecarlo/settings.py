""""""

# Standard library modules.
import os
import enum

# Third party modules.
import h5py

# Local modules.
import pymontecarlo
from pymontecarlo.util.path import get_config_dir
from pymontecarlo.util.signal import Signal
from pymontecarlo.entity import EntityBase, EntryHDF5IOMixin

# Globals and constants variables.


class XrayNotation(enum.Enum):
    IUPAC = "iupac"
    SIEGBAHN = "siegbahn"


class Settings(EntityBase, EntryHDF5IOMixin):

    DEFAULT_FILENAME = "settings.h5"

    settings_changed = Signal()

    def __init__(self):
        # Units
        self.preferred_units = {}

        # X-ray line
        self.preferred_xray_notation = XrayNotation.IUPAC

        # Paths
        self._opendir = None
        self._savedir = None

    @classmethod
    def read(cls, filepath=None):
        if filepath is None:
            filepath = os.path.join(get_config_dir(), cls.DEFAULT_FILENAME)
            if not os.path.exists(filepath):
                return cls()

        return super().read(filepath)

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
        if not hasattr(q, "units"):
            q = pymontecarlo.unit_registry.Quantity(q, units)

        _, base_unit = pymontecarlo.unit_registry._get_base_units(q.units)

        try:
            preferred_unit = self.preferred_units[base_unit]
            return q.to(preferred_unit)
        except KeyError:
            return q.to(base_unit)

    @property
    def opendir(self):
        return self._opendir or self._savedir or os.getcwd()

    @opendir.setter
    def opendir(self, dirpath):
        self._opendir = dirpath

    @property
    def savedir(self):
        return self._savedir or self._opendir or os.getcwd()

    @savedir.setter
    def savedir(self, dirpath):
        self._savedir = dirpath

    # region HDF5

    DATASET_PREFERRED_UNITS = "preferred units"
    ATTR_PREFERRED_XRAY_NOTATION = "preferred x-ray notation"
    ATTR_OPENDIR = "opendir"
    ATTR_SAVEDIR = "savedir"

    @classmethod
    def parse_hdf5(cls, group):
        obj = cls()

        units = [str(value) for value in group[cls.DATASET_PREFERRED_UNITS].asstr()]
        for unit in units:
            obj.set_preferred_unit(unit)

        obj.preferred_xray_notation = cls._parse_hdf5(
            group, cls.ATTR_PREFERRED_XRAY_NOTATION, XrayNotation
        )
        obj.opendir = cls._parse_hdf5(group, cls.ATTR_OPENDIR, str)
        obj.savedir = cls._parse_hdf5(group, cls.ATTR_SAVEDIR, str)

        return obj

    def convert_hdf5(self, group):
        super().convert_hdf5(group)

        shape = (len(self.preferred_units),)
        dtype = h5py.special_dtype(vlen=str)
        dataset = group.create_dataset(self.DATASET_PREFERRED_UNITS, shape, dtype)
        dataset[:] = list(map(str, self.preferred_units.values()))

        self._convert_hdf5(
            group, self.ATTR_PREFERRED_XRAY_NOTATION, self.preferred_xray_notation
        )
        self._convert_hdf5(group, self.ATTR_OPENDIR, self.opendir)
        self._convert_hdf5(group, self.ATTR_SAVEDIR, self.savedir)


# endregion
