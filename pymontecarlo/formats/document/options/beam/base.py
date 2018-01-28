""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.handler import DocumentHandlerBase
from pymontecarlo.options.beam.base import BeamBase
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class BeamDocumentHandlerBase(DocumentHandlerBase):

    def convert(self, beam, builder):
        super().convert(beam, builder)

        builder.add_title(camelcase_to_words(type(beam).__name__))

        description = builder.require_description('beam')
        description.add_item('Energy', beam.energy_eV, 'eV', BeamBase.ENERGY_TOLERANCE_eV)
        description.add_item('Particle', beam.particle)
