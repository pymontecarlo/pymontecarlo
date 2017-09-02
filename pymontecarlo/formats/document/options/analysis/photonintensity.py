""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.analysis.photon import PhotonAnalysisDocumentHandler
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis

# Globals and constants variables.

class PhotonIntensityAnalysisDocumentHandler(PhotonAnalysisDocumentHandler):

    @property
    def CLASS(self):
        return PhotonIntensityAnalysis
