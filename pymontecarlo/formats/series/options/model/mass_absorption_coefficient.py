""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.model.mass_absorption_coefficient import MassAbsorptionCoefficientModel

# Globals and constants variables.

class MassAbsorptionCoefficientModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model):
        s = super().convert(model)

        column = NamedSeriesColumn('mass absorption coefficient', 'mac')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return MassAbsorptionCoefficientModel