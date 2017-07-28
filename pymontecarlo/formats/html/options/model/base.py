""""""

# Standard library modules.
from collections import OrderedDict

# Third party modules.

# Local modules.
from pymontecarlo.formats.html.base import TableHtmlHandler
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class ModelHtmlHandler(TableHtmlHandler):

    def convert_rows(self, model, settings):
        row = OrderedDict()

        key = self._create_label(settings, 'Category')
        value = self._format_value(settings, camelcase_to_words(self.CLASS.__name__[:-5]))
        row[key] = value

        key = self._create_label(settings, 'Model')
        value = self._format_value(settings, model.fullname)
        row[key] = value

        key = self._create_label(settings, 'Reference')
        value = self._format_value(settings, model.reference)
        row[key] = value

        rows = super().convert_rows(model, settings)
        rows.append(row)
        return rows
