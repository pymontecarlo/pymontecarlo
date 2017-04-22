""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.model.base import ModelHtmlHandler
from pymontecarlo.options.model.energy_loss import EnergyLossModel

# Globals and constants variables.

class EnergyLossModelHtmlHandler(ModelHtmlHandler):

    @property
    def CLASS(self):
        return EnergyLossModel
