""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.options.sample.base import LayeredSampleHtmlHandler
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample

# Globals and constants variables.

class VerticalLayerSampleHtmlHandler(LayeredSampleHtmlHandler):

    def convert(self, sample, level=1):
        root = super().convert(sample, level=1)

        root += self._create_header(level, 'Substrates')

        dl = tags.dl()
        dl += self._create_description('Left material', sample.left_material.name)
        dl += self._create_description('Right material', sample.right_material.name)
        dl += self._create_description('Depth', sample.depth_m, 'm', VerticalLayerSample.DEPTH_TOLERANCE_m)
        root += dl

        return root

    @property
    def CLASS(self):
        return VerticalLayerSample
