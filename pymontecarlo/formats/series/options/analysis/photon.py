""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.analysis.base import AnalysisSeriesHandler

# Globals and constants variables.

class PhotonAnalysisSeriesHandler(AnalysisSeriesHandler):

    def convert(self, analysis):
        return super().convert(analysis)
