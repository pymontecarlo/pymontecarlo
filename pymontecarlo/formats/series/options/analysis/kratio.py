""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.analysis.photon import PhotonAnalysisSeriesHandler
from pymontecarlo.options.analysis.kratio import KRatioAnalysis

# Globals and constants variables.

class KRatioAnalysisSeriesHandler(PhotonAnalysisSeriesHandler):

    @property
    def CLASS(self):
        return KRatioAnalysis
