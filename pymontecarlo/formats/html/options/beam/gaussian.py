""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.beam.base import BeamHtmlHandler
from pymontecarlo.options.beam.gaussian import GaussianBeam

# Globals and constants variables.

class GaussianBeamHtmlHandler(BeamHtmlHandler):

    def convert(self, beam, level=1):
        root = super().convert(beam, level=1)

        dl = root.getElementsByTagName('dl')[-1]
        dl += self._create_description('Diameter', beam.diameter_m, 'm', GaussianBeam.DIAMETER_TOLERANCE_m)
        dl += self._create_description('Initial x position', beam.x0_m, 'm', GaussianBeam.POSITION_TOLERANCE_m)
        dl += self._create_description('Initial y position', beam.y0_m, 'm', GaussianBeam.POSITION_TOLERANCE_m)

        return root

    @property
    def CLASS(self):
        return GaussianBeam
