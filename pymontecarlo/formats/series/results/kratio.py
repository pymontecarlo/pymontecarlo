""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.helper import LazyXrayLineFormat
from pymontecarlo.formats.series.results.photon import PhotonResultSeriesHandlerBase
from pymontecarlo.results.kratio import KRatioResult

# Globals and constants variables.

class KRatioResultSeriesHandler(PhotonResultSeriesHandlerBase):

    def convert(self, result, builder):
        super().convert(result, builder)

        for xrayline, q in result.items():
            name = abbrev = LazyXrayLineFormat(xrayline)
            builder.add_column(name, abbrev, q.n)
            builder.add_column(name, abbrev, q.s, error=True)

    @property
    def CLASS(self):
        return KRatioResult
