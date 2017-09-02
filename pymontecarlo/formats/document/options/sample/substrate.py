""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.sample.base import SampleDocumentHandler
from pymontecarlo.options.sample.substrate import SubstrateSample

# Globals and constants variables.

class SubstrateSampleDocumentHandler(SampleDocumentHandler):

    @property
    def CLASS(self):
        return SubstrateSample
