""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import LayeredSampleHandlerBase
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample

# Globals and constants variables.

class VerticalLayerSampleSeriesHandler(LayeredSampleHandlerBase):

    def convert(self, sample, builder):
        super().convert(sample, builder)
        builder.add_object(sample.left_material, 'left substrate ', 'left ')
        builder.add_object(sample.right_material, 'right substrate ', 'right ')
        builder.add_column('vertical layers depth', 'zmax', sample.depth_m, 'm', VerticalLayerSample.DEPTH_TOLERANCE_m)

    @property
    def CLASS(self):
        return VerticalLayerSample
