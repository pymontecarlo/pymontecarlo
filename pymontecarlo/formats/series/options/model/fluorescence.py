""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.model.fluorescence import FluorescenceModel
# Globals and constants variables.

class FluorescenceModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model, settings):
        s = super().convert(model, settings)

        column = NamedSeriesColumn(settings, 'fluorescence', 'fluo')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return FluorescenceModel
