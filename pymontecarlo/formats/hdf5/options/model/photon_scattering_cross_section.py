""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.model.base import ModelHDF5Handler
from pymontecarlo.options.model.photon_scattering_cross_section import PhotonScatteringCrossSectionModel

# Globals and constants variables.

class PhotonScatteringCrossSectionModelHDF5Handler(ModelHDF5Handler):

    @property
    def CLASS(self):
        return PhotonScatteringCrossSectionModel