""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.model.base import ModelHtmlHandler
from pymontecarlo.options.model.ionization_potential import IonizationPotentialModel

# Globals and constants variables.

class IonizationPotentialModelHtmlHandler(ModelHtmlHandler):

    @property
    def CLASS(self):
        return IonizationPotentialModel