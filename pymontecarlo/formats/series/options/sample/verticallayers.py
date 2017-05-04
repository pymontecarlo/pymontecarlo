""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import LayeredSampleHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample

# Globals and constants variables.

class VerticalLayerSampleSeriesHandler(LayeredSampleHandler):

    def convert(self, sample):
        s = super().convert(sample)

        s_material = self._find_and_convert(sample.left_material, 'left substrate ', 'left ')
        s = s.append(s_material)

        s_material = self._find_and_convert(sample.right_material, 'right substrate ', 'right ')
        s = s.append(s_material)

        column = NamedSeriesColumn('vertical layers depth', 'zmax', 'm', VerticalLayerSample.DEPTH_TOLERANCE_m)
        s[column] = sample.depth_m

        return s

    @property
    def CLASS(self):
        return VerticalLayerSample
