""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.options.limit.base import LimitHtmlHandler
from pymontecarlo.options.limit.showers import ShowersLimit

# Globals and constants variables.

class ShowersLimitHtmlHandler(LimitHtmlHandler):

    def convert(self, limit, level=1):
        root = super().convert(limit)

        dl = tags.dl()
        dl += self._create_description('Number of trajectories', limit.number_trajectories)
        root += dl

        return root

    @property
    def CLASS(self):
        return ShowersLimit
