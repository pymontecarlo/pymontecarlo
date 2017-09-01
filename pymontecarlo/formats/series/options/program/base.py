""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler, NamedSeriesColumn

# Globals and constants variables.

class ProgramSeriesHandler(SeriesHandler):

    def convert(self, program):
        s = super().convert(program)

        column = NamedSeriesColumn('program', 'prog')
        s[column] = program.name

        return s
