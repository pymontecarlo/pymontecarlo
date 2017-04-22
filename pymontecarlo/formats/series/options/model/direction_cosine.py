""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.formats.series.base import SeriesColumn
from pymontecarlo.options.model.direction_cosine import DirectionCosineModel

# Globals and constants variables.

class DirectionCosineModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model):
        s = super().convert(model)

        column = SeriesColumn('direction cosine', 'cosine')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return DirectionCosineModel