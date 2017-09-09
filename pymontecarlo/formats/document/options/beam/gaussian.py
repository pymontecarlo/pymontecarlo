""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.beam.cylindrical import CylindricalBeamDocumentHandler
from pymontecarlo.options.beam.gaussian import GaussianBeam

# Globals and constants variables.

class GaussianBeamDocumentHandler(CylindricalBeamDocumentHandler):

    @property
    def CLASS(self):
        return GaussianBeam
