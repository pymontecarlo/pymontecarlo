""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandler

# Globals and constants variables.

class ProgramSeriesHandler(SeriesHandler):

    def create_builder(self, program):
        builder = super().create_builder(program)
        builder.add_column('program', 'prog', program.name)
        return builder
