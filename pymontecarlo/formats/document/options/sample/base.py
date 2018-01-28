""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.handler import DocumentHandler
from pymontecarlo.options.sample.base import SampleBase, Layer
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class SampleDocumentHandler(DocumentHandler):

    def convert(self, sample, builder):
        super().convert(sample, builder)

        builder.add_title(camelcase_to_words(type(sample).__name__))

        section = builder.add_section()
        section.add_title('Orientation')
        description = section.require_description('angles')
        description.add_item('Tilt angle', sample.tilt_rad, 'rad', SampleBase.TILT_TOLERANCE_rad)
        description.add_item('Azimuth rotation', sample.azimuth_rad, 'rad', SampleBase.AZIMUTH_TOLERANCE_rad)

        section = builder.add_section()
        section.add_title('Material' if len(sample.materials) < 2 else 'Materials')
        for material in sample.materials:
            section.add_object(material)

class LayerDocumentHandler(DocumentHandler):

    def convert(self, layer, builder):
        super().convert(layer, builder)

        table = builder.require_table('layers')

        table.add_column('Material')
        table.add_column('Thickness', 'm', Layer.THICKNESS_TOLERANCE_m)

        row = {'Material': layer.material.name,
               'Thickness': layer.thickness_m}
        table.add_row(row)

    @property
    def CLASS(self):
        return Layer

class LayeredSampleDocumentHandler(SampleDocumentHandler):

    def convert(self, sample, builder):
        super().convert(sample, builder)

        section = builder.add_section()
        section.add_title('Layer' if len(sample.layers) < 2 else 'Layers')
        for layer in sample.layers:
            section.add_object(layer)
