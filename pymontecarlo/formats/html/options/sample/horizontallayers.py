""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.options.sample.base import LayeredSampleHtmlHandler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample

# Globals and constants variables.

class HorizontalLayerSampleHtmlHandler(LayeredSampleHtmlHandler):

    def convert(self, sample, settings, level=1):
        root = super().convert(sample, settings, level)

        root += self._create_header(level, 'Substrate')

        dl = tags.dl()
        dl += self._create_description(settings, 'Material', sample.substrate_material.name)
        root += dl

        return root

    @property
    def CLASS(self):
        return HorizontalLayerSample
