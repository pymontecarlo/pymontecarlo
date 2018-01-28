""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandlerBase
from pymontecarlo.options.beam.base import BeamBase

# Globals and constants variables.

class BeamSeriesHandlerBase(SeriesHandlerBase):

    def convert(self, beam, builder):
        super().convert(beam, builder)
        builder.add_column('beam energy', 'E0', beam.energy_eV, 'eV', BeamBase.ENERGY_TOLERANCE_eV)
        builder.add_column('beam particle', 'par', str(beam.particle))
