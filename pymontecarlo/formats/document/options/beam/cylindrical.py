""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.beam.base import BeamDocumentHandlerBase
from pymontecarlo.options.beam.cylindrical import CylindricalBeam

# Globals and constants variables.

class CylindricalBeamDocumentHandler(BeamDocumentHandlerBase):

    def convert(self, beam, builder):
        super().convert(beam, builder)

        description = builder.require_description('beam')
        description.add_item('Diameter', beam.diameter_m, 'm', CylindricalBeam.DIAMETER_TOLERANCE_m)
        description.add_item('Initial x position', beam.x0_m, 'm', CylindricalBeam.POSITION_TOLERANCE_m)
        description.add_item('Initial y position', beam.y0_m, 'm', CylindricalBeam.POSITION_TOLERANCE_m)

    @property
    def CLASS(self):
        return CylindricalBeam
