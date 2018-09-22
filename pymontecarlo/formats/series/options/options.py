""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandlerBase
from pymontecarlo.options.options import Options

# Globals and constants variables.

class OptionsSeriesHandler(SeriesHandlerBase):

    def convert(self, options, builder):
        super().convert(options, builder)

        builder.add_object(options.program)
        builder.add_object(options.beam)
        builder.add_object(options.sample)

        for detector in options.detectors:
            builder.add_object(detector)

        for analysis in options.analyses:
            builder.add_object(analysis)

        for tag in options.tags:
            builder.add_column(tag, tag, True)

    @property
    def CLASS(self):
        return Options
