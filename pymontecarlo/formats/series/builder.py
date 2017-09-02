""""""

# Standard library modules.

# Third party modules.
import pandas as pd

# Local modules.
from pymontecarlo.formats.series.entrypoint import find_convert_serieshandler
from pymontecarlo.formats.builder import FormatBuilder

# Globals and constants variables.

class SeriesBuilder(FormatBuilder):

    def add_column(self, name, abbrev, value, unit=None, tolerance=None, error=False):
        self._add_datum(name, abbrev, value, unit, tolerance, error)

    def add_object(self, obj, prefix_name='', prefix_abbrev=''):
        handler = find_convert_serieshandler(obj)

        builder = self.__class__(self.settings)
        handler.convert(obj, builder)

        self._add_builder(builder, prefix_name, prefix_abbrev)

    def build(self):
        s = pd.Series()

        for datum in self.data:
            label = self._format_label(datum)
            value = self._format_value(datum)
            s[label] = value

        return s
