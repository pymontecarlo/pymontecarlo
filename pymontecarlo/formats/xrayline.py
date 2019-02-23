""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.settings import XrayNotation
from pymontecarlo.formats.base import LazyFormat

# Globals and constants variables.

class LazyXrayLineFormat(LazyFormat):

    def __init__(self, xrayline):
        self.xrayline = xrayline

    def format(self, settings):
        if settings.preferred_xray_notation == XrayNotation.SIEGBAHN:
            return self.xrayline.siegbahn
        else:
            return self.xrayline.iupac