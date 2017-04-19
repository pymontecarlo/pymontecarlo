""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5Handler
from pymontecarlo.options.model.elastic_cross_section import ElasticCrossSectionModel

# Globals and constants variables.

class ElasticCrossSectionModelHDF5Handler(ModelHDF5Handler):

    @property
    def CLASS(self):
        return ElasticCrossSectionModel
