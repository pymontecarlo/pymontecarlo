""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.results.photon import \
    PhotonResultSeriesHandler, XrayLineSeriesColumn
from pymontecarlo.results.kratio import KRatioResult

# Globals and constants variables.

class KRatioResultSeriesHandler(PhotonResultSeriesHandler):

    def convert(self, result):
        s = super().convert(result)

        for xrayline, q in result.items():
            column = XrayLineSeriesColumn(xrayline)
            s[column] = q

        return s

    @property
    def CLASS(self):
        return KRatioResult
