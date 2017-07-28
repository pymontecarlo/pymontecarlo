""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.model.inelastic_cross_section import InelasticCrossSectionModel

# Globals and constants variables.

class InelasticCrossSectionModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model, settings):
        s = super().convert(model, settings)

        column = NamedSeriesColumn(settings, 'inelastic cross-section', 'inelastic')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return InelasticCrossSectionModel
