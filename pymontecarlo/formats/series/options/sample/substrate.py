""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import SampleSeriesHandler
from pymontecarlo.options.sample.substrate import SubstrateSample

# Globals and constants variables.

class SubstrateSampleSeriesHandler(SampleSeriesHandler):

    def create_builder(self, sample):
        builder = super().create_builder(sample)
        builder.add_object(sample.material, 'substrate ', 'subs ')
        return builder

    @property
    def CLASS(self):
        return SubstrateSample
