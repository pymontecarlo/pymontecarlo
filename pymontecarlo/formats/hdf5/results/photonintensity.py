""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.results.photon import PhotonResultHDF5Handler
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult

# Globals and constants variables.

class PhotonIntensityResultHDF5Handler(PhotonResultHDF5Handler):

    DATASET_INTENSITIES = 'intensities'

    def _parse_values(self, group):
        return self._parse_values_0d(self.DATASET_INTENSITIES, group)

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.DATASET_INTENSITIES in group

    def _convert_values(self, values, group):
        return self._convert_values_0d(values, self.DATASET_INTENSITIES, group)

class GeneratedPhotonIntensityResultHDF5Handler(PhotonIntensityResultHDF5Handler):

    @property
    def CLASS(self):
        return GeneratedPhotonIntensityResult

class EmittedPhotonIntensityResultHDF5Handler(PhotonIntensityResultHDF5Handler):

    @property
    def CLASS(self):
        return EmittedPhotonIntensityResult