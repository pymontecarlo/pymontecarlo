"""
Base classes for limits
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import Builder

# Globals and constants variables.

class Limit(object):

    def __eq__(self, other):
        return True

class LimitBuilder(Builder):
    pass
