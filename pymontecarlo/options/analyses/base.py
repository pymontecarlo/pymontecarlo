"""
Base analysis.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.options.option import Option

# Globals and constants variables.

class Analysis(Option):

    @abc.abstractmethod
    def apply(self, options):
        return []

    @abc.abstractmethod
    def calculate(self, simulations):
        pass
