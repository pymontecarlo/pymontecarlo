""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.options.limit.base import LimitHtmlHandler
from pymontecarlo.options.limit.uncertainty import UncertaintyLimit

# Globals and constants variables.

class UncertaintyLimitHtmlHandler(LimitHtmlHandler):

    def convert(self, limit, level=1):
        root = super().convert(limit)

        dl = tags.dl()
        dl += self._create_description('X-ray line', limit.xrayline)
        dl += self._create_description('Detector', limit.detector.name)
        dl += self._create_description('Uncertainty', limit.uncertainty, tolerance=UncertaintyLimit.UNCERTAINTY_TOLERANCE)
        root += dl

        return root

    @property
    def CLASS(self):
        return UncertaintyLimit
