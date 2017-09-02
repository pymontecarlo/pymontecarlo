""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import LayeredSampleHandler
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample

# Globals and constants variables.

class VerticalLayerSampleSeriesHandler(LayeredSampleHandler):

    def create_builder(self, sample):
        builder = super().create_builder(sample)
        builder.add_object(sample.left_material, 'left substrate ', 'left ')
        builder.add_object(sample.right_material, 'right substrate ', 'right ')
        builder.add_column('vertical layers depth', 'zmax', sample.depth_m, 'm', VerticalLayerSample.DEPTH_TOLERANCE_m)
        return builder

    @property
    def CLASS(self):
        return VerticalLayerSample
