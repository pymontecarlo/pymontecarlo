""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.base import SeriesColumn
from pymontecarlo.formats.series.results.base import ResultSeriesHandler
from pymontecarlo.util.xrayline import XrayLine

# Globals and constants variables.

class XrayLineSeriesColumn(SeriesColumn):

    def __init__(self, xrayline, unit=None, tolerance=None):
        name = abbrev = str(xrayline)
        super().__init__(name, abbrev, unit, tolerance)
        self._xrayline = xrayline

    def __eq__(self, other):
        if isinstance(other, XrayLine):
            return self.xrayline == other
        return type(self) == type(other) and self.xrayline == other.xrayline

    def __hash__(self):
        return hash(self.xrayline)

    @property
    def name(self):
        return str(self.xrayline)

    @property
    def abbrev(self):
        return str(self.xrayline)

    @property
    def xrayline(self):
        return self._xrayline

class PhotonResultSeriesHandler(ResultSeriesHandler):
    pass
