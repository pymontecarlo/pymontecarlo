"""
Settings for pymontecarlo
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.fileformat.reader import HDF5ReaderMixin
from pymontecarlo.fileformat.writer import HDF5WriterMixin

# Globals and constants variables.

class Settings(HDF5ReaderMixin, HDF5WriterMixin):

    def __init__(self, programs=None):
        if programs is None:
            programs = []
        self.programs = programs

