""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5HandlerBase
from pymontecarlo.options.model.fluorescence import FluorescenceModel
# Globals and constants variables.

class FluorescenceModelHDF5Handler(ModelHDF5HandlerBase):

    @property
    def CLASS(self):
        return FluorescenceModel
