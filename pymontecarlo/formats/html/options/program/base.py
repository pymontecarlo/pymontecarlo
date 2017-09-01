""""""

# Standard library modules.

# Third party modules.
import dominate.tags as tags

# Local modules.
from pymontecarlo.formats.html.base import HtmlHandler

# Globals and constants variables.

class ProgramHtmlHandler(HtmlHandler):

    def convert(self, program, settings, level=1):
        root = super().convert(program, settings, level)

        dl = tags.dl()
        dl += self._create_description(settings, 'Name', program.name)
        root += dl

        return root

