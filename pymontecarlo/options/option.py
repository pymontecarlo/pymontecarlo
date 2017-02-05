"""
Base option class
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class Option(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __eq__(self, other):
        return True
