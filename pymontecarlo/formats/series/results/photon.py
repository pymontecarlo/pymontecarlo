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
        name = abbrev = str(xrayline)
        super().__init__(name, abbrev, unit, tolerance)
        self._xrayline = xrayline
        self._prefix = ''
        self._prefix_abbrev = ''

    def __eq__(self, other):
        if isinstance(other, XrayLine):
            return self.xrayline == other
        return type(self) == type(other) and self.xrayline == other.xrayline

    def __hash__(self):
        return hash((self._prefix, self.xrayline))

    def with_prefix(self, prefix, prefix_abbrev=None):
        column = self.__class__(self.xrayline, self.unit, self.tolerance)
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
    def xrayline(self):
        return self._xrayline

class PhotonResultSeriesHandler(ResultSeriesHandler):
    pass
