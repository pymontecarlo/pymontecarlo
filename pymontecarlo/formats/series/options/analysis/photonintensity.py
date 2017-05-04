""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.analysis.photon import PhotonAnalysisSeriesHandler
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis

# Globals and constants variables.

class PhotonIntensityAnalysisSeriesHandler(PhotonAnalysisSeriesHandler):

    @property
    def CLASS(self):
        return PhotonIntensityAnalysis
