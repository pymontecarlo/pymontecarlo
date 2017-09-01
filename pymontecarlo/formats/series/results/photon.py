""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.base import SeriesColumn
from pymontecarlo.formats.series.results.base import ResultSeriesHandler
from pymontecarlo.util.xrayline import XrayLine
from pymontecarlo.settings import XrayNotation

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

    def format_name(self, settings):
        if settings.preferred_xray_notation == XrayNotation.SIEGBAHN:
            return self.xrayline.siegbahn
        else:
            return self.xrayline.iupac

    @property
    def name(self):
        return self.xrayline.iupac

    @property
    def abbrev(self):
        return self.name

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
