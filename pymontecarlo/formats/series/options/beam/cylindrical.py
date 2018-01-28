""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.beam.base import BeamSeriesHandlerBase
from pymontecarlo.options.beam.cylindrical import CylindricalBeam

# Globals and constants variables.

class CylindricalBeamSeriesHandler(BeamSeriesHandlerBase):

    def convert(self, beam, builder):
        super().convert(beam, builder)
        builder.add_column('beam diameter', 'd0', beam.diameter_m, 'm', CylindricalBeam.DIAMETER_TOLERANCE_m)
        builder.add_column('beam initial x position', 'x0', beam.x0_m, 'm', CylindricalBeam.POSITION_TOLERANCE_m)
        builder.add_column('beam initial y position', 'y0', beam.y0_m, 'm', CylindricalBeam.POSITION_TOLERANCE_m)

    @property
    def CLASS(self):
        return CylindricalBeam

