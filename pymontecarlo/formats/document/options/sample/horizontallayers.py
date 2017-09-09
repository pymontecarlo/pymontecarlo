""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.sample.base import LayeredSampleDocumentHandler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample

# Globals and constants variables.

class HorizontalLayerSampleDocumentHandler(LayeredSampleDocumentHandler):

    def convert(self, sample, builder):
        super().convert(sample, builder)

        section = builder.add_section()
        section.add_title('Substrate')
        description = section.require_description('substrate')
        description.add_item('Material', sample.substrate_material.name)

    @property
    def CLASS(self):
        return HorizontalLayerSample
