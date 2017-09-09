""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import SampleSeriesHandler
from pymontecarlo.options.sample.substrate import SubstrateSample

# Globals and constants variables.

class SubstrateSampleSeriesHandler(SampleSeriesHandler):

    def convert(self, sample, builder):
        super().convert(sample, builder)
        builder.add_object(sample.material, 'substrate ', 'subs ')

    @property
    def CLASS(self):
        return SubstrateSample
