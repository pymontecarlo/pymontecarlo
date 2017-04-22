""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import SampleSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.sample.sphere import SphereSample

# Globals and constants variables.

class SphereSampleSeriesHandler(SampleSeriesHandler):

    def convert(self, sample):
        s = super().convert(sample)

        s_material = self._find_and_convert(sample.material, 'sphere ', 'sphere ')
        s = s.append(s_material)

        column = NamedSeriesColumn('sphere diameter', 'd', 'm', SphereSample.DIAMETER_TOLERANCE_m)
        s[column] = sample.diameter_m

        return s

    @property
    def CLASS(self):
        return SphereSample
