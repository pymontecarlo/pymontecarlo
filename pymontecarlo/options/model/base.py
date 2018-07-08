"""
Base models.
"""

# Standard library modules.
import enum

# Third party modules.

# Local modules.

# Globals and constants variables.

# ModelBase should inherit OptionBase but this prevents a model class to
# be pickled or copied. Since enum.Enum automatically implements __eq__
# there is no need to inherit OptionBase.
class ModelBase(enum.Enum):

    def __init__(self, fullname, reference=''):
        self.fullname = fullname
        self.reference = reference

    def __str__(self):
        return self.fullname
