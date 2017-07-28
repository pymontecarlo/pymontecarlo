""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.beam.base import BeamSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.beam.cylindrical import CylindricalBeam

# Globals and constants variables.

class CylindricalBeamSeriesHandler(BeamSeriesHandler):

    def convert(self, beam, settings):
        s = super().convert(beam, settings)

        column = NamedSeriesColumn(settings, 'beam diameter', 'd0', 'm', CylindricalBeam.DIAMETER_TOLERANCE_m)
        s[column] = beam.diameter_m

        column = NamedSeriesColumn(settings, 'beam initial x position', 'x0', 'm', CylindricalBeam.POSITION_TOLERANCE_m)
        s[column] = beam.x0_m

        column = NamedSeriesColumn(settings, 'beam initial y position', 'y0', 'm', CylindricalBeam.POSITION_TOLERANCE_m)
        s[column] = beam.y0_m

        return s

    @property
    def CLASS(self):
        return CylindricalBeam

