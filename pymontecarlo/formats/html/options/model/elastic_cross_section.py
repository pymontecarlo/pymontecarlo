""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.model.base import ModelHtmlHandler
from pymontecarlo.options.model.elastic_cross_section import ElasticCrossSectionModel

# Globals and constants variables.

class ElasticCrossSectionModelHtmlHandler(ModelHtmlHandler):

    @property
    def CLASS(self):
        return ElasticCrossSectionModel
