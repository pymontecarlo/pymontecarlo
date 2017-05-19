""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.beam.cylindrical import \
    CylindricalBeamHtmlHandler
from pymontecarlo.options.beam.gaussian import GaussianBeam

# Globals and constants variables.

class GaussianBeamHtmlHandler(CylindricalBeamHtmlHandler):

    @property
    def CLASS(self):
        return GaussianBeam
