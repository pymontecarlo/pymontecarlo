""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5Handler
from pymontecarlo.options.model.bremsstrahlung_emission import BremsstrahlungEmissionModel

# Globals and constants variables.

class BremsstrahlungEmissionModelHDF5Handler(ModelHDF5Handler):

    @property
    def CLASS(self):
        return BremsstrahlungEmissionModel
