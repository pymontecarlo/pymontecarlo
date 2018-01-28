""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.handler import DocumentHandlerBase
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class AnalysisDocumentHandlerBase(DocumentHandlerBase):

    def convert(self, analysis, builder):
        super().convert(analysis, builder)

        builder.add_title(camelcase_to_words(type(analysis).__name__))