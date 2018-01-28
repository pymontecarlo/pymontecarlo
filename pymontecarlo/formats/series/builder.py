""""""

# Standard library modules.

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.formats.series.entrypoint import find_convert_serieshandler
from pymontecarlo.formats.builder import FormatBuilderBase

# Globals and constants variables.

class SeriesBuilder(FormatBuilderBase):

    def __init__(self, settings, abbreviate_name=False, format_number=False):
        super().__init__(settings, abbreviate_name, format_number)
        self.data = []

    def add_column(self, name, abbrev, value, unit=None, tolerance=None, error=False):
        datum = self._create_datum(name, abbrev, value, unit, tolerance, error)
        self.data.append(datum)

    def add_object(self, obj, prefix_name='', prefix_abbrev=''):
        handler = find_convert_serieshandler(obj)
        builder = self.__class__(self.settings)
        handler.convert(obj, builder)

        prefix_abbrev = prefix_abbrev or prefix_name

        for datum in builder.data:
            datum = datum.copy()
            datum['prefix_name'] = datum['prefix_name'] + prefix_name
            datum['prefix_abbrev'] = datum['prefix_abbrev'] + prefix_abbrev
            self.data.append(datum)

    def build(self):
        s = pd.Series()

        for datum in self.data:
            label = self._format_label(datum)
            value = self._format_value(datum)
            s[label] = value

        return s

    def gettolerances(self):
        tolerances = {}

        for datum in self.data:
            label = self._format_label(datum)

            unit = datum['unit']
            tolerance = datum['tolerance']

            if tolerance is not None:
                tolerances[label] = self._convert_value(tolerance, unit)

        return tolerances
