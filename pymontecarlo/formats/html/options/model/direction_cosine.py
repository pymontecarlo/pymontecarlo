""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.model.base import ModelHtmlHandler
from pymontecarlo.options.model.direction_cosine import DirectionCosineModel

# Globals and constants variables.

class DirectionCosineModelHtmlHandler(ModelHtmlHandler):

    @property
    def CLASS(self):
        return DirectionCosineModel
