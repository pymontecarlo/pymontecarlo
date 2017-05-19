""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.beam.cylindrical import \
    CylindricalBeamSeriesHandler
from pymontecarlo.options.beam.gaussian import GaussianBeam

# Globals and constants variables.

class GaussianBeamSeriesHandler(CylindricalBeamSeriesHandler):

    @property
    def CLASS(self):
        return GaussianBeam

