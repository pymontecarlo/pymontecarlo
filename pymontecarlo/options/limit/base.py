"""
Base classes for limits
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.util.interface import Builder
from pymontecarlo.options.option import Option

# Globals and constants variables.

class Limit(Option):
    pass

class LimitBuilder(Builder):
    pass
