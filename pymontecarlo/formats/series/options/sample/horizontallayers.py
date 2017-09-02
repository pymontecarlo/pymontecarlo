""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import LayeredSampleHandler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample

# Globals and constants variables.

class HorizontalLayerSampleSeriesHandler(LayeredSampleHandler):

    def convert(self, sample, builder):
        super().convert(sample, builder)
        builder.add_object(sample.substrate_material, 'substrate ', 'subs ')

    @property
    def CLASS(self):
        return HorizontalLayerSample
