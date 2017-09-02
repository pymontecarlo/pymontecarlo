""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.handler import DocumentHandler

# Globals and constants variables.

class ProgramDocumentHandler(DocumentHandler):

    def convert(self, program, builder):
        super().convert(program, builder)

        builder.add_title(program.name)
