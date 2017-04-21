""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler
from pymontecarlo.options.beam.base import Beam

# Globals and constants variables.

class BeamSeriesHandler(SeriesHandler):

    def convert(self, beam):
        s = super().convert(beam)

        column = self._create_column('beam energy', 'E0', 'eV', Beam.ENERGY_TOLERANCE_eV)
        s[column] = beam.energy_eV

        column = self._create_column('beam particle', 'par')
        s[column] = str(beam.particle)

        return s
