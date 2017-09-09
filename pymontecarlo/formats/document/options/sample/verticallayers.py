""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.sample.base import LayeredSampleDocumentHandler
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample

# Globals and constants variables.

class VerticalLayerSampleDocumentHandler(LayeredSampleDocumentHandler):

    def convert(self, sample, builder):
        super().convert(sample, builder)

        section = builder.add_section()
        section.add_title('Substrates')
        description = section.require_description('vertical layer')
        description.add_item('Left material', sample.left_material.name)
        description.add_item('Right material', sample.right_material.name)
        description.add_item('Depth', sample.depth_m, 'm', VerticalLayerSample.DEPTH_TOLERANCE_m)

    @property
    def CLASS(self):
        return VerticalLayerSample
