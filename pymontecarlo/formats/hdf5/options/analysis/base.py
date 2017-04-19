""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.base import HDF5Handler
from pymontecarlo.formats.hdf5.options.detector.base import DetectorHDF5HandlerMixin

# Globals and constants variables.

class AnalysisHDF5Handler(HDF5Handler, DetectorHDF5HandlerMixin):
    pass