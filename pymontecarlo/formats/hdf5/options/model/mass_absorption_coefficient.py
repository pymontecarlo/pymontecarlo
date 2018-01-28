""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5HandlerBase
from pymontecarlo.options.model.mass_absorption_coefficient import MassAbsorptionCoefficientModel

# Globals and constants variables.

class MassAbsorptionCoefficientModelHDF5Handler(ModelHDF5HandlerBase):

    @property
    def CLASS(self):
        return MassAbsorptionCoefficientModel