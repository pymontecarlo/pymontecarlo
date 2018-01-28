""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.analysis.base import AnalysisSeriesHandlerBase

# Globals and constants variables.

class PhotonAnalysisSeriesHandlerBase(AnalysisSeriesHandlerBase):

    def convert(self, analysis, builder):
        return super().convert(analysis, builder)
