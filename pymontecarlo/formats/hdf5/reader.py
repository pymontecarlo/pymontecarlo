""""""

# Standard library modules.

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.util.future import FutureExecutor
from pymontecarlo.formats.hdf5.base import find_parse_hdf5handler

# Globals and constants variables.

def read(filepath):
    with h5py.File(filepath, 'r') as f:
        return find_parse_hdf5handler(f).parse(f)

class HDF5Reader(FutureExecutor):

    def submit(self, filepath):
        def target(token, filepath):
            return read(filepath)
        return self._submit(target, filepath)

class HDF5ReaderMixin:

    @classmethod
    def read(cls, filepath):
        return read(filepath)

class HDF5FutureReaderMixin:

    @classmethod
    def read(cls, filepath):
        with HDF5Reader() as executor:
            future = executor.submit(filepath)
            return future.result()