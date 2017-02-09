"""
Interfaces.
"""

# Standard library modules.
import abc
from collections import OrderedDict

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

class DataRowCreator(metaclass=abc.ABCMeta):

    #@abc.abstractmethod
    def create_datarow(self):
        return OrderedDict()
