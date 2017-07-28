""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import LayeredSampleHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample

# Globals and constants variables.

class VerticalLayerSampleSeriesHandler(LayeredSampleHandler):

    def convert(self, sample, settings):
        s = super().convert(sample, settings)

        s_material = self._find_and_convert(sample.left_material, settings, 'left substrate ', 'left ')
        s = s.append(s_material)

        s_material = self._find_and_convert(sample.right_material, settings, 'right substrate ', 'right ')
        s = s.append(s_material)

        column = NamedSeriesColumn(settings, 'vertical layers depth', 'zmax', 'm', VerticalLayerSample.DEPTH_TOLERANCE_m)
        s[column] = sample.depth_m

        return s

    @property
    def CLASS(self):
        return VerticalLayerSample
