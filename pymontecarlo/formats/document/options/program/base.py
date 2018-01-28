""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.handler import DocumentHandlerBase

# Globals and constants variables.

class ProgramDocumentHandlerBase(DocumentHandlerBase):

    def convert(self, program, builder):
        super().convert(program, builder)

        builder.add_title(program.name)
