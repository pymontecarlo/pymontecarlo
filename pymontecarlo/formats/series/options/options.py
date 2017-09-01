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

        s_program = self._find_and_convert(options.program)
        s = s.append(s_program)

        s_beam = self._find_and_convert(options.beam)
        s = s.append(s_beam)

        s_sample = self._find_and_convert(options.sample)
        s = s.append(s_sample)

        for detector in options.detectors:
            s_detector = self._find_and_convert(detector)
            s = s.append(s_detector)

        for analysis in options.analyses:
            s_analysis = self._find_and_convert(analysis)
            s = s.append(s_analysis)

        return s

    @property
    def CLASS(self):
        return Options
