""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5HandlerBase
from pymontecarlo.options.model.energy_loss import EnergyLossModel

# Globals and constants variables.

class EnergyLossModelHDF5Handler(ModelHDF5HandlerBase):

    @property
    def CLASS(self):
        return EnergyLossModel
