""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandler
from pymontecarlo.options.options import Options

# Globals and constants variables.

class OptionsSeriesHandler(SeriesHandler):

    def create_builder(self, options):
        builder = super().create_builder(options)

        builder.add_object(options.program)
        builder.add_object(options.beam)
        builder.add_object(options.sample)

        for detector in options.detectors:
            builder.add_object(detector)

        for analysis in options.analyses:
            builder.add_object(analysis)

        return builder

    @property
    def CLASS(self):
        return Options
