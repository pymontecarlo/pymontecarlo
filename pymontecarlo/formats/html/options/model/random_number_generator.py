""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.model.base import ModelHtmlHandler
from pymontecarlo.options.model.random_number_generator import RandomNumberGeneratorModel

# Globals and constants variables.

class RandomNumberGeneratorModelHtmlHandler(ModelHtmlHandler):

    @property
    def CLASS(self):
        return RandomNumberGeneratorModel