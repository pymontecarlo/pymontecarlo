""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandler

# Globals and constants variables.

class ProgramSeriesHandler(SeriesHandler):

    def _convert(self, program):
        builder = super()._convert(program)
        builder.add_column('program', 'prog', program.name)
        return builder
