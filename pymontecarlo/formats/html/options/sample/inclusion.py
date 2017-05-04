""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.options.sample.base import SampleHtmlHandler
from pymontecarlo.options.sample.inclusion import InclusionSample

# Globals and constants variables.

class InclusionSampleHtmlHandler(SampleHtmlHandler):

    def convert(self, sample, level=1):
        root = super().convert(sample, level)

        root += self._create_header(level, 'Substrate')

        dl = tags.dl()
        dl += self._create_description('Material', sample.substrate_material.name)
        root += dl

        root += self._create_header(level, 'Inclusion')

        dl = tags.dl()
        dl += self._create_description('Material', sample.inclusion_material.name)
        dl += self._create_description('Diameter', sample.inclusion_diameter_m, 'm', InclusionSample.INCLUSION_DIAMETER_TOLERANCE_m)
        root += dl

        return root

    @property
    def CLASS(self):
        return InclusionSample
