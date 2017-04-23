""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.base import SeriesColumn
from pymontecarlo.formats.series.results.base import ResultSeriesHandler
from pymontecarlo.util.xrayline import XrayLine

# Globals and constants variables.

class SeriesXrayLineColumn(SeriesColumn):

    def __init__(self, xrayline, unit=None, tolerance=None):
        super().__init__()
        self._xrayline = xrayline
        self._unit = unit
        self._tolerance = tolerance

    def __eq__(self, other):
        if isinstance(other, XrayLine):
            return self.xrayline == other
        return type(self) == type(other) and self.xrayline == other.xrayline

    def __hash__(self):
        return hash(self.xrayline)

    @property
    def name(self):
        return self.xrayline.name

    @property
    def abbrev(self):
        return self.xrayline.name

    @property
    def unit(self):
        return self._unit

    @property
    def tolerance(self):
        return self._tolerance

    @property
    def xrayline(self):
        return self._xrayline

class PhotonResultSeriesHandler(ResultSeriesHandler):
    pass
