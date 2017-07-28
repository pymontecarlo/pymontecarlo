""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler, NamedSeriesColumn
from pymontecarlo.options.options import Options

# Globals and constants variables.

class OptionsSeriesHandler(SeriesHandler):

    def convert(self, options, settings):
        s = super().convert(options, settings)

        column = NamedSeriesColumn(settings, 'program', 'prog')
        s[column] = options.program.name

        s_beam = self._find_and_convert(options.beam, settings)
        s = s.append(s_beam)

        s_sample = self._find_and_convert(options.sample, settings)
        s = s.append(s_sample)

        for detector in options.detectors:
            s_detector = self._find_and_convert(detector, settings)
            s = s.append(s_detector)

        for analysis in options.analyses:
            s_analysis = self._find_and_convert(analysis, settings)
            s = s.append(s_analysis)

        for limit in options.limits:
            s_limit = self._find_and_convert(limit, settings)
            s = s.append(s_limit)

        for model in options.models:
            s_model = self._find_and_convert(model, settings)
            s = s.append(s_model)

        return s

    @property
    def CLASS(self):
        return Options
