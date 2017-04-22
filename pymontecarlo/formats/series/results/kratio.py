""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.results.photon import \
    PhotonResultSeriesHandler, SeriesXrayLineColumn
from pymontecarlo.results.kratio import KRatioResult

# Globals and constants variables.

class KRatioResultSeriesHandler(PhotonResultSeriesHandler):

    def convert(self, result):
        s = super().convert(result)

        for xrayline, q in result.items():
            column = SeriesXrayLineColumn(xrayline)
            s[column] = q

        return s

    @property
    def CLASS(self):
        return KRatioResult
