""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.limit.base import LimitSeriesHandler
from pymontecarlo.options.limit.uncertainty import UncertaintyLimit

# Globals and constants variables.

class UncertaintyLimitSeriesHandler(LimitSeriesHandler):

    def convert(self, limit):
        s = super().convert(limit)

        s_detector = self._convert_serieshandlers(limit.detector)
        s = s.append(s_detector)

        column = self._create_column('uncertainty value', 'unc', tolerance=UncertaintyLimit.UNCERTAINTY_TOLERANCE)
        s[column] = limit.uncertainty

        return s

    @property
    def CLASS(self):
        return UncertaintyLimit
