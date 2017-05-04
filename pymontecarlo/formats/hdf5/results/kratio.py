""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.results.photon import PhotonResultHDF5Handler
from pymontecarlo.results.kratio import KRatioResult

# Globals and constants variables.

class KRatioResultHDF5Handler(PhotonResultHDF5Handler):

    DATASET_KRATIOS = 'kratios'

    def _parse_values(self, group):
        return self._parse_values_0d(self.DATASET_KRATIOS, group)

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.DATASET_KRATIOS in group

    def _convert_values(self, values, group):
        return self._convert_values_0d(values, self.DATASET_KRATIOS, group)

    @property
    def CLASS(self):
        return KRatioResult
