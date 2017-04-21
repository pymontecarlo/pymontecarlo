""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.options.model.inelastic_cross_section import InelasticCrossSectionModel

# Globals and constants variables.

class InelasticCrossSectionModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model):
        s = super().convert(model)

        column = self._create_column('inelastic cross-section', 'inelastic')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return InelasticCrossSectionModel
