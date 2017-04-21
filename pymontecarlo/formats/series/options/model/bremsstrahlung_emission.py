""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.options.model.bremsstrahlung_emission import BremsstrahlungEmissionModel

# Globals and constants variables.

class BremsstrahlungEmissionModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model):
        s = super().convert(model)

        column = self._create_column('bremsstrahlung emission', 'bremss')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return BremsstrahlungEmissionModel
