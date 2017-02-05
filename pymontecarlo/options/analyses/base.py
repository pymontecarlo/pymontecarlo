"""
Base analysis.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class Analysis(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def apply(self, options):
        pass

    @abc.abstractmethod
    def calculate(self, simulations):
        pass
