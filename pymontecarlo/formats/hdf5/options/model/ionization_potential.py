""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5Handler
from pymontecarlo.options.model.ionization_potential import IonizationPotentialModel

# Globals and constants variables.

class IonizationPotentialModelHDF5Handler(ModelHDF5Handler):

    @property
    def CLASS(self):
        return IonizationPotentialModel