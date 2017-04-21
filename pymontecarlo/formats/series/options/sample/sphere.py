""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import SampleSeriesHandler
from pymontecarlo.options.sample.sphere import SphereSample

# Globals and constants variables.

class SphereSampleSeriesHandler(SampleSeriesHandler):

    def convert(self, sample):
        s = super().convert(sample)

        s_material = self._convert_serieshandlers(sample.material)
        s_material = self._update_with_prefix(s_material, 'sphere ', 'sphere ')
        s = s.append(s_material)

        column = self._create_column('sphere diameter', 'd', 'm', SphereSample.DIAMETER_TOLERANCE_m)
        s[column] = sample.diameter_m

        return s

    @property
    def CLASS(self):
        return SphereSample
