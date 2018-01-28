""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5HandlerBase
from pymontecarlo.options.model.random_number_generator import RandomNumberGeneratorModel

# Globals and constants variables.

class RandomNumberGeneratorModelHDF5Handler(ModelHDF5HandlerBase):

    @property
    def CLASS(self):
        return RandomNumberGeneratorModel