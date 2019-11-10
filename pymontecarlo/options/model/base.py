"""
Base models.
"""

__all__ = ["convert_models_document"]

# Standard library modules.
import enum

# Third party modules.

# Local modules.
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

# ModelBase should inherit OptionBase but this prevents a model class to
# be pickled or copied. Since enum.Enum automatically implements __eq__
# there is no need to inherit OptionBase.
class ModelBase(enum.Enum):
    def __init__(self, fullname, reference=""):
        self.fullname = fullname
        self.reference = reference

    def __str__(self):
        return self.fullname


def convert_models_document(builder, *models):
    table = builder.require_table("models")

    table.add_column("Category")
    table.add_column("Model")
    table.add_column("Reference")

    for model in models:
        row = {
            "Category": camelcase_to_words(model.__class__.__name__[:-5]),
            "Model": model.fullname,
            "Reference": model.reference,
        }
        table.add_row(row)
