""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandler

# Globals and constants variables.

class ProgramSeriesHandler(SeriesHandler):

    def convert(self, program, builder):
        super().convert(program, builder)
        builder.add_column('program', 'prog', program.name)
