""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.model.base import ModelSeriesHandler
from pymontecarlo.formats.series.base import NamedSeriesColumn
from pymontecarlo.options.model.ionization_potential import IonizationPotentialModel

# Globals and constants variables.

class IonizationPotentialModelSeriesHandler(ModelSeriesHandler):

    def convert(self, model):
        s = super().convert(model)

        column = NamedSeriesColumn('ionization potential', 'ioniz. potential')
        s[column] = model.name

        return s

    @property
    def CLASS(self):
        return IonizationPotentialModel