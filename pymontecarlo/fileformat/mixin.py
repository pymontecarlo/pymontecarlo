""""""

# Standard library modules.

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.fileformat.base import find_parse_handler, find_convert_handler

# Globals and constants variables.

class ReadWriteMixin:

    @classmethod
    def read(cls, filepath):
        with h5py.File(filepath, 'r') as f:
            return find_parse_handler(f).parse(f)

    def write(self, filepath):
        with h5py.File(filepath, 'w') as f:
            find_convert_handler(self, f).convert(self, f)
