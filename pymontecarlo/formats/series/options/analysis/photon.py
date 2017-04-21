""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.analysis.base import AnalysisSeriesHandler

# Globals and constants variables.

class PhotonAnalysisSeriesHandler(AnalysisSeriesHandler):

    def convert(self, analysis):
        s = super().convert(analysis)

        s_detector = self._convert_serieshandlers(analysis.photon_detector)
        s = s.append(s_detector)

        return s
