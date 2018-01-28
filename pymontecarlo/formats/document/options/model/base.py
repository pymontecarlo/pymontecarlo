""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.handler import DocumentHandler
from pymontecarlo.options.model.base import ModelBase
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class ModelDocumentHandler(DocumentHandler):

    def convert(self, model, builder):
        super().convert(model, builder)

        table = builder.require_table('models')

        table.add_column('Category')
        table.add_column('Model')
        table.add_column('Reference')

        row = {'Category': camelcase_to_words(type(model).__name__[:-5]),
               'Model': model.fullname,
               'Reference': model.reference}
        table.add_row(row)

    def can_convert(self, obj):
        return isinstance(obj, self.CLASS)

    @property
    def CLASS(self):
        return ModelBase
