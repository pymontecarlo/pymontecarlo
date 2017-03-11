""""""

# Standard library modules.

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.util.future import FutureExecutor
from pymontecarlo.fileformat.base import find_convert_hdf5handler

# Globals and constants variables.

class HDF5Writer(FutureExecutor):

    def submit(self, obj, filepath):
        def target(token, obj, filepath):
            with h5py.File(filepath, 'w') as f:
                return find_convert_hdf5handler(obj, f).convert(obj, f)
        return self._submit(target, obj, filepath)

class HDF5WriterMixin:

    def write(self, filepath):
        with HDF5Writer() as executor:
            future = executor.submit(self, filepath)
            return future.result()
