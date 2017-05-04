""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5Handler
from pymontecarlo.options.model.random_number_generator import RandomNumberGeneratorModel

# Globals and constants variables.

class RandomNumberGeneratorModelHDF5Handler(ModelHDF5Handler):

    @property
    def CLASS(self):
        return RandomNumberGeneratorModel