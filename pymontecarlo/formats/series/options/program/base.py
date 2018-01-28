""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandlerBase

# Globals and constants variables.

class ProgramSeriesHandlerBase(SeriesHandlerBase):

    def convert(self, program, builder):
        super().convert(program, builder)
        builder.add_column('program', 'prog', program.name)
