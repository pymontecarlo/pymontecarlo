""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import SampleSeriesHandler
from pymontecarlo.options.sample.substrate import SubstrateSample

# Globals and constants variables.

class SubstrateSampleSeriesHandler(SampleSeriesHandler):

    def convert(self, sample, settings):
        s = super().convert(sample, settings)

        s_material = self._find_and_convert(sample.material, settings, 'substrate ', 'subs ')
        s = s.append(s_material)

        return s

    @property
    def CLASS(self):
        return SubstrateSample
