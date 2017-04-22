""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.options.sample.base import SampleHtmlHandler
from pymontecarlo.options.sample.sphere import SphereSample

# Globals and constants variables.

class SphereSampleHtmlHandler(SampleHtmlHandler):

    def convert(self, sample, level=1):
        root = super().convert(sample, level)

        root += self._create_header(level, 'Sphere')

        dl = tags.dl()
        dl += self._create_description('Material', sample.material.name)
        dl += self._create_description('Diameter', sample.diameter_m, 'm', SphereSample.DIAMETER_TOLERANCE_m)
        root += dl

        return root

    @property
    def CLASS(self):
        return SphereSample
