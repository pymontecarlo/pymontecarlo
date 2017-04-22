""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.model.base import ModelHtmlHandler
from pymontecarlo.options.model.ionization_cross_section import IonizationCrossSectionModel
# Globals and constants variables.

class IonizationCrossSectionModelHtmlHandler(ModelHtmlHandler):

    @property
    def CLASS(self):
        return IonizationCrossSectionModel