""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.sample.base import SampleSeriesHandler
from pymontecarlo.options.sample.inclusion import InclusionSample

# Globals and constants variables.

class InclusionSampleSeriesHandler(SampleSeriesHandler):

    def convert(self, sample):
        s = super().convert(sample)

        s_material = self._convert_serieshandlers(sample.substrate_material)
        s_material = self._update_with_prefix(s_material, 'substrate ', 'subs. ')
        s = s.append(s_material)

        s_material = self._convert_serieshandlers(sample.inclusion_material)
        s_material = self._update_with_prefix(s_material, 'inclusion ', 'incl. ')
        s = s.append(s_material)

        column = self._create_column('inclusion diameter', 'd', 'm', InclusionSample.INCLUSION_DIAMETER_TOLERANCE_m)
        s[column] = sample.inclusion_diameter_m

        return s

    @property
    def CLASS(self):
        return InclusionSample
