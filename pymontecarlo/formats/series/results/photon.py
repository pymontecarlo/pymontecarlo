""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.results.base import ResultSeriesHandler
from pymontecarlo.settings import XrayNotation

# Globals and constants variables.

class xrayline_name_func:

    def __init__(self, xrayline):
        self.xrayline = xrayline

    def __call__(self, settings):
        if settings.preferred_xray_notation == XrayNotation.SIEGBAHN:
            return self.xrayline.siegbahn
        else:
            return self.xrayline.iupac

class PhotonResultSeriesHandler(ResultSeriesHandler):
    pass
