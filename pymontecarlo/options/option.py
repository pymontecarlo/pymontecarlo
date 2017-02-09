"""
Base option class
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class Option(metaclass=abc.ABCMeta):
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

    @abc.abstractproperty
    def parameters(self):
        return set()
