""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.options.sample.base import SampleHtmlHandler
from pymontecarlo.options.sample.substrate import SubstrateSample

# Globals and constants variables.

class SubstrateSampleHtmlHandler(SampleHtmlHandler):

    @property
    def CLASS(self):
        return SubstrateSample
