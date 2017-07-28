""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.base import HtmlHandler
from pymontecarlo.options.beam.base import Beam

# Globals and constants variables.

class BeamHtmlHandler(HtmlHandler):

    def convert(self, beam, settings, level=1):
        root = super().convert(beam, settings, level)

        dl = tags.dl()
        dl += self._create_description(settings, 'Energy', beam.energy_eV, 'eV', Beam.ENERGY_TOLERANCE_eV)
        dl += self._create_description(settings, 'Particle', beam.particle)
        root += dl

        return root
