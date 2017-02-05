"""
Base analysis.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class Analysis(metaclass=abc.ABCMeta):

    def __eq__(self, other):
        return True

    @abc.abstractmethod
    def apply(self, options):
        return []

    @abc.abstractmethod
    def calculate(self, simulations):
        pass
