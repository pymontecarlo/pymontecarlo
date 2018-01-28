""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import SampleSeriesHandlerBase
from pymontecarlo.options.sample.inclusion import InclusionSample

# Globals and constants variables.

class InclusionSampleSeriesHandler(SampleSeriesHandlerBase):

    def convert(self, sample, builder):
        super().convert(sample, builder)
        builder.add_object(sample.substrate_material, 'substrate ', 'subs ')
        builder.add_object(sample.inclusion_material, 'inclusion ', 'incl ')
        builder.add_column('inclusion diameter', 'd', sample.inclusion_diameter_m, 'm', InclusionSample.INCLUSION_DIAMETER_TOLERANCE_m)

    @property
    def CLASS(self):
        return InclusionSample
