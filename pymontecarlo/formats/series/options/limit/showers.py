""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.limit.base import LimitSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.limit.showers import ShowersLimit

# Globals and constants variables.

class ShowersLimitSeriesHandler(LimitSeriesHandler):

    def convert(self, limit):
        s = super().convert(limit)

        column = NamedSeriesColumn('number of trajectories', 'N')
        s[column] = limit.number_trajectories

        return s

    @property
    def CLASS(self):
        return ShowersLimit
