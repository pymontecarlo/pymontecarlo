""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5HandlerBase
from pymontecarlo.options.model.direction_cosine import DirectionCosineModel

# Globals and constants variables.

class DirectionCosineModelHDF5Handler(ModelHDF5HandlerBase):

    @property
    def CLASS(self):
        return DirectionCosineModel
