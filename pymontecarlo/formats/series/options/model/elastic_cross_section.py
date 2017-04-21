""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.options.model.elastic_cross_section import ElasticCrossSectionModel

# Globals and constants variables.

class ElasticCrossSectionModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model):
        s = super().convert(model)

        column = self._create_column('elastic cross-section', 'elastic')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return ElasticCrossSectionModel
