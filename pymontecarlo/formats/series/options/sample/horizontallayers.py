""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import LayeredSampleHandler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample

# Globals and constants variables.

class HorizontalLayerSampleSeriesHandler(LayeredSampleHandler):

    def create_builder(self, sample):
        builder = super().create_builder(sample)
        builder.add_object(sample.substrate_material, 'substrate ', 'subs ')
        return builder

    @property
    def CLASS(self):
        return HorizontalLayerSample
