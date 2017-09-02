""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandler
from pymontecarlo.options.beam.base import Beam

# Globals and constants variables.

class BeamSeriesHandler(SeriesHandler):

    def create_builder(self, beam):
        builder = super().create_builder(beam)
        builder.add_column('beam energy', 'E0', beam.energy_eV, 'eV', Beam.ENERGY_TOLERANCE_eV)
        builder.add_column('beam particle', 'par', str(beam.particle))
        return builder
