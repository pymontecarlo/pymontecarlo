""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.analysis.base import AnalysisSeriesHandler

# Globals and constants variables.

class PhotonAnalysisSeriesHandler(AnalysisSeriesHandler):

    def create_builder(self, analysis):
        return super().create_builder(analysis)
