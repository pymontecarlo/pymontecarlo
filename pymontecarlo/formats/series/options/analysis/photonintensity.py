""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.analysis.photon import PhotonAnalysisSeriesHandlerBase
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis

# Globals and constants variables.

class PhotonIntensityAnalysisSeriesHandler(PhotonAnalysisSeriesHandlerBase):

    @property
    def CLASS(self):
        return PhotonIntensityAnalysis
