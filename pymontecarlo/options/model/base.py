"""
Base models.
"""

# Standard library modules.
import abc
import enum

# Third party modules.

# Local modules.
from pymontecarlo.options.base import Option

# Globals and constants variables.

class ModelMeta(enum.EnumMeta, abc.ABCMeta):
    pass

class Model(Option, enum.Enum, metaclass=ModelMeta):

    def __init__(self, fullname, reference=''):
        self.fullname = fullname
        self.reference = reference

    def __eq__(self, other):
        # NOTE: Must be implemented from Option,
        # but should only used equality from Enum
        return enum.Enum.__eq__(self, other)

    def __str__(self):
        return self.fullname
