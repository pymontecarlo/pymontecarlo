""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.analysis.photon import PhotonAnalysisHDF5Handler
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis

# Globals and constants variables.

class PhotonIntensityAnalysisHDF5Handler(PhotonAnalysisHDF5Handler):

    def parse(self, group):
        photon_detector = self._parse_photon_detector(group)
        return self.CLASS(photon_detector)

    def convert(self, analysis, group):
        super().convert(analysis, group)

    @property
    def CLASS(self):
        return PhotonIntensityAnalysis
