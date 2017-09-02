""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import SampleSeriesHandler
from pymontecarlo.options.sample.sphere import SphereSample

# Globals and constants variables.

class SphereSampleSeriesHandler(SampleSeriesHandler):

    def _convert(self, sample):
        builder = super()._convert(sample)
        builder.add_object(sample.material, 'sphere ', 'sphere ')
        builder.add_column('sphere diameter', 'd', sample.diameter_m, 'm', SphereSample.DIAMETER_TOLERANCE_m)
        return builder

    @property
    def CLASS(self):
        return SphereSample
