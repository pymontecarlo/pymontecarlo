""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.analysis.photon import PhotonAnalysisHtmlHandler
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis

# Globals and constants variables.

class PhotonIntensityAnalysisHtmlHandler(PhotonAnalysisHtmlHandler):

    @property
    def CLASS(self):
        return PhotonIntensityAnalysis
