""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.model.base import ModelHtmlHandler
from pymontecarlo.options.model.inelastic_cross_section import InelasticCrossSectionModel

# Globals and constants variables.

class InelasticCrossSectionModelHtmlHandler(ModelHtmlHandler):

    @property
    def CLASS(self):
        return InelasticCrossSectionModel
