""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.handler import DocumentHandler
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class AnalysisDocumentHandler(DocumentHandler):

    def convert(self, analysis, builder):
        super().convert(analysis, builder)

        builder.add_title(camelcase_to_words(type(analysis).__name__))