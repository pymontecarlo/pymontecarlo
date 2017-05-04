""""""

# Standard library modules.

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.util.future import FutureExecutor
from pymontecarlo.formats.hdf5.base import find_convert_hdf5handler

# Globals and constants variables.

def write(obj, filepath):
    with h5py.File(filepath, 'w') as f:
        return find_convert_hdf5handler(obj, f).convert(obj, f)

class HDF5Writer(FutureExecutor):

    def submit(self, obj, filepath):
        def target(token, obj, filepath):
            write(obj, filepath)
        return self._submit(target, obj, filepath)

class HDF5WriterMixin:

    def write(self, filepath):
        write(self, filepath)

class HDF5FutureWriterMixin:

    def write(self, filepath):
        with HDF5Writer() as executor:
            future = executor.submit(self, filepath)
            return future.result()
