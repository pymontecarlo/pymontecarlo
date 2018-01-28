""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.sample.base import SampleDocumentHandlerBase
from pymontecarlo.options.sample.substrate import SubstrateSample

# Globals and constants variables.

class SubstrateSampleDocumentHandler(SampleDocumentHandlerBase):

    @property
    def CLASS(self):
        return SubstrateSample
