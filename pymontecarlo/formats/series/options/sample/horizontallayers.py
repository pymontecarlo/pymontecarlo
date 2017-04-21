""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import LayeredSampleHandler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample

# Globals and constants variables.

class HorizontalLayerSampleSeriesHandler(LayeredSampleHandler):

    def convert(self, sample):
        s = super().convert(sample)

        s_material = self._convert_serieshandlers(sample.substrate_material)
        s_material = self._update_with_prefix(s_material, 'substrate ', 'subs. ')
        s = s.append(s_material)

        return s

    @property
    def CLASS(self):
        return HorizontalLayerSample
