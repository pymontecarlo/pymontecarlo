""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler
from pymontecarlo.options.options import Options

# Globals and constants variables.

class OptionsSeriesHandler(SeriesHandler):

    def convert(self, options):
        s = super().convert(options)

        column = self._create_column('program', 'prog')
        s[column] = options.program.getidentifier()

        s_beam = self._convert_serieshandlers(options.beam)
        s = s.append(s_beam)

        s_sample = self._convert_serieshandlers(options.sample)
        s = s.append(s_sample)

        for analysis in options.analyses:
            s_analysis = self._convert_serieshandlers(analysis)
            s = s.append(s_analysis)

        for limit in options.limits:
            s_limit = self._convert_serieshandlers(limit)
            s = s.append(s_limit)

        for model in options.models:
            s_model = self._convert_serieshandlers(model)
            s = s.append(s_model)

        return s

    @property
    def CLASS(self):
        return Options
