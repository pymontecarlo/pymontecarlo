"""
Interfaces.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class Builder(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def build(self):
        raise NotImplementedError