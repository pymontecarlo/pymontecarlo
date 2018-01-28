""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.handler import SeriesHandler
from pymontecarlo.options.model.base import ModelBase
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class ModelSeriesHandler(SeriesHandler):

    def convert(self, model, builder):
        super().convert(model, builder)

        name = camelcase_to_words(type(model).__name__).lower()
        abbrev = name[:6]
        builder.add_column(name, abbrev, model.name)

    def can_convert(self, obj):
        return isinstance(obj, self.CLASS)

    @property
    def CLASS(self):
        return ModelBase

