"""
Base detector.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.base import OptionBase, OptionBuilderBase

# Globals and constants variables.

class DetectorBase(OptionBase):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def __eq__(self, other):
        return super().__eq__(other) and self.name == other.name

class DetectorBuilderBase(OptionBuilderBase):
    pass
