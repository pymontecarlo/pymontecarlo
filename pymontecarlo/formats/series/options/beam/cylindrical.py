""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.beam.base import BeamSeriesHandler
from pymontecarlo.options.beam.cylindrical import CylindricalBeam

# Globals and constants variables.

class CylindricalBeamSeriesHandler(BeamSeriesHandler):

    def create_builder(self, beam):
        builder = super().create_builder(beam)
        builder.add_column('beam diameter', 'd0', beam.diameter_m, 'm', CylindricalBeam.DIAMETER_TOLERANCE_m)
        builder.add_column('beam initial x position', 'x0', beam.x0_m, 'm', CylindricalBeam.POSITION_TOLERANCE_m)
        builder.add_column('beam initial y position', 'y0', beam.y0_m, 'm', CylindricalBeam.POSITION_TOLERANCE_m)
        return builder

    @property
    def CLASS(self):
        return CylindricalBeam

