""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import SampleSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.sample.inclusion import InclusionSample

# Globals and constants variables.

class InclusionSampleSeriesHandler(SampleSeriesHandler):

    def convert(self, sample):
        s = super().convert(sample)

        s_material = self._find_and_convert(sample.substrate_material, 'substrate ', 'subs ')
        s = s.append(s_material)

        s_material = self._find_and_convert(sample.inclusion_material, 'inclusion ', 'incl ')
        s = s.append(s_material)

        column = NamedSeriesColumn('inclusion diameter', 'd', 'm', InclusionSample.INCLUSION_DIAMETER_TOLERANCE_m)
        s[column] = sample.inclusion_diameter_m

        return s

    @property
    def CLASS(self):
        return InclusionSample
