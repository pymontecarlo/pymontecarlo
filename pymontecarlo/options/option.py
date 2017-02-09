"""
Base option class
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.util.interface import DataRowCreator

# Globals and constants variables.

class Option(DataRowCreator, metaclass=abc.ABCMeta):
    """
    Base class of all the options.
    All derived classes should implement
    
        - method :meth:`__eq__`
        - property :var:`property`
        - class variable :var:`NAME` (use lower case when possible)
        - class variable :var:`DESCRIPTION`
    """

    NAME = None
    DESCRIPTION = None

    @abc.abstractmethod
    def __eq__(self, other):
        return type(other) == type(self)
