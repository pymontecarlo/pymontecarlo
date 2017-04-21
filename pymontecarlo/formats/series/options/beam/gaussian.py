""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.beam.base import BeamSeriesHandler
from pymontecarlo.options.beam.gaussian import GaussianBeam

# Globals and constants variables.

class GaussianBeamSeriesHandler(BeamSeriesHandler):

    def convert(self, beam):
        s = super().convert(beam)

        column = self._create_column('beam diameter', 'd0', 'm', GaussianBeam.DIAMETER_TOLERANCE_m)
        s[column] = beam.diameter_m

        column = self._create_column('beam initial x position', 'x0', 'm', GaussianBeam.POSITION_TOLERANCE_m)
        s[column] = beam.x0_m

        column = self._create_column('beam initial y position', 'y0', 'm', GaussianBeam.POSITION_TOLERANCE_m)
        s[column] = beam.y0_m

        return s

    @property
    def CLASS(self):
        return GaussianBeam

