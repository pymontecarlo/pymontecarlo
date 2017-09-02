""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandler
from pymontecarlo.options.model.base import Model
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class ModelSeriesHandler(SeriesHandler):

    def create_builder(self, model):
        builder = super().create_builder(model)

        name = camelcase_to_words(type(model).__name__).lower()
        abbrev = name[:6]
        builder.add_column(name, abbrev, model.name)

        return builder

    def can_convert(self, obj):
        return isinstance(obj, self.CLASS)

    @property
    def CLASS(self):
        return Model

