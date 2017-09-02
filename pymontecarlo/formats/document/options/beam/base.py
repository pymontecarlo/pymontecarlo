""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.handler import DocumentHandler
from pymontecarlo.options.beam.base import Beam
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class BeamDocumentHandler(DocumentHandler):

    def convert(self, beam, builder):
        super().convert(beam, builder)

        builder.add_title(camelcase_to_words(type(beam).__name__))

        description = builder.require_description('beam')
        description.add_item('Energy', beam.energy_eV, 'eV', Beam.ENERGY_TOLERANCE_eV)
        description.add_item('Particle', beam.particle)
