""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler, NamedSeriesColumn

# Globals and constants variables.

class ProgramSeriesHandler(SeriesHandler):

    def convert(self, program, settings):
        s = super().convert(program, settings)

        column = NamedSeriesColumn(settings, 'program', 'prog')
        s[column] = program.name

        return s
