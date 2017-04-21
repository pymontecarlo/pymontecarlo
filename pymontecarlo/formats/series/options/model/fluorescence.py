""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.options.model.fluorescence import FluorescenceModel
# Globals and constants variables.

class FluorescenceModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model):
        s = super().convert(model)

        column = self._create_column('fluorescence', 'fluo')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return FluorescenceModel
