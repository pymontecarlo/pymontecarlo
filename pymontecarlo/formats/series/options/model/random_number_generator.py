""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.model.random_number_generator import RandomNumberGeneratorModel

# Globals and constants variables.

class RandomNumberGeneratorModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model):
        s = super().convert(model)

        column = NamedSeriesColumn('random number generator', 'random')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return RandomNumberGeneratorModel