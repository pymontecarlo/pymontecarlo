""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5Handler
from pymontecarlo.options.model.inelastic_cross_section import InelasticCrossSectionModel

# Globals and constants variables.

class InelasticCrossSectionModelHDF5Handler(ModelHDF5Handler):

    @property
    def CLASS(self):
        return InelasticCrossSectionModel
