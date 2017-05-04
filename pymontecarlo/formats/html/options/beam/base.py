""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.base import HtmlHandler
from pymontecarlo.options.beam.base import Beam

# Globals and constants variables.

class BeamHtmlHandler(HtmlHandler):

    def convert(self, beam, level=1):
        root = super().convert(beam, level=1)

        dl = tags.dl()
        dl += self._create_description('Energy', beam.energy_eV, 'eV', Beam.ENERGY_TOLERANCE_eV)
        dl += self._create_description('Particle', beam.particle)
        root += dl

        return root
