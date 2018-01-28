""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5HandlerBase
from pymontecarlo.options.model.ionization_cross_section import IonizationCrossSectionModel
# Globals and constants variables.

class IonizationCrossSectionModelHDF5Handler(ModelHDF5HandlerBase):

    @property
    def CLASS(self):
        return IonizationCrossSectionModel