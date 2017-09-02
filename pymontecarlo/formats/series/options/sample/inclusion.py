""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import SampleSeriesHandler
from pymontecarlo.options.sample.inclusion import InclusionSample

# Globals and constants variables.

class InclusionSampleSeriesHandler(SampleSeriesHandler):

    def create_builder(self, sample):
        builder = super().create_builder(sample)
        builder.add_object(sample.substrate_material, 'substrate ', 'subs ')
        builder.add_object(sample.inclusion_material, 'inclusion ', 'incl ')
        builder.add_column('inclusion diameter', 'd', sample.inclusion_diameter_m, 'm', InclusionSample.INCLUSION_DIAMETER_TOLERANCE_m)
        return builder

    @property
    def CLASS(self):
        return InclusionSample
