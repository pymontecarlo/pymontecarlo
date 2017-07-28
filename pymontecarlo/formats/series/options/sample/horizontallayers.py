""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import LayeredSampleHandler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample

# Globals and constants variables.

class HorizontalLayerSampleSeriesHandler(LayeredSampleHandler):

    def convert(self, sample, settings):
        s = super().convert(sample, settings)

        s_material = self._find_and_convert(sample.substrate_material, settings, 'substrate ', 'subs ')
        s = s.append(s_material)

        return s

    @property
    def CLASS(self):
        return HorizontalLayerSample
