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
        self._prefix = ''
        self._prefix_abbrev = ''

    def __eq__(self, other):
        if isinstance(other, XrayLine):
            return self.xrayline == other and not self._prefix
        return type(self) == type(other) and \
            self.xrayline == other.xrayline and \
            self._prefix == other._prefix

    def __hash__(self):
        return hash((self._prefix, self.xrayline))

    def with_prefix(self, prefix, prefix_abbrev=None):
        column = SeriesXrayLineColumn(self.xrayline, self.unit, self.tolerance)
        column._prefix = prefix
        column._prefix_abbrev = prefix_abbrev or prefix
        return column

    @property
    def name(self):
        return self._prefix + str(self.xrayline)

    @property
    def abbrev(self):
        return self._prefix_abbrev + str(self.xrayline)

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
