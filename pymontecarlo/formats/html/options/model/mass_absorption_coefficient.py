""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.model.base import ModelHtmlHandler
from pymontecarlo.options.model.mass_absorption_coefficient import MassAbsorptionCoefficientModel

# Globals and constants variables.

class MassAbsorptionCoefficientModelHtmlHandler(ModelHtmlHandler):

    @property
    def CLASS(self):
        return MassAbsorptionCoefficientModel