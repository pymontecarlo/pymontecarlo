""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.base import SeriesHandler, NamedSeriesColumn
from pymontecarlo.options.beam.base import Beam

# Globals and constants variables.

class BeamSeriesHandler(SeriesHandler):

    def convert(self, beam, settings):
        s = super().convert(beam, settings)

        column = NamedSeriesColumn(settings, 'beam energy', 'E0', 'eV', Beam.ENERGY_TOLERANCE_eV)
        s[column] = beam.energy_eV

        column = NamedSeriesColumn(settings, 'beam particle', 'par')
        s[column] = str(beam.particle)

        return s
