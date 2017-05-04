""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.model.base import ModelHtmlHandler
from pymontecarlo.options.model.fluorescence import FluorescenceModel

# Globals and constants variables.

class FluorescenceModelHtmlHandler(ModelHtmlHandler):

    @property
    def CLASS(self):
        return FluorescenceModel
