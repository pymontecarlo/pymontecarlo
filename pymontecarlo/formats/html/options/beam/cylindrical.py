""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.beam.base import BeamHtmlHandler
from pymontecarlo.options.beam.cylindrical import CylindricalBeam

# Globals and constants variables.

class CylindricalBeamHtmlHandler(BeamHtmlHandler):

    def convert(self, beam, settings, level=1):
        root = super().convert(beam, settings, level)

        dl = root.getElementsByTagName('dl')[-1]
        dl += self._create_description(settings, 'Diameter', beam.diameter_m, 'm', CylindricalBeam.DIAMETER_TOLERANCE_m)
        dl += self._create_description(settings, 'Initial x position', beam.x0_m, 'm', CylindricalBeam.POSITION_TOLERANCE_m)
        dl += self._create_description(settings, 'Initial y position', beam.y0_m, 'm', CylindricalBeam.POSITION_TOLERANCE_m)

        return root

    @property
    def CLASS(self):
        return CylindricalBeam
