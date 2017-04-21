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
    """

    @abc.abstractmethod
    def __eq__(self, other):
        """
        Returns whether two options are equal. 
        Each option should implement some tolerance for the comparison of
        float values.
        """
        return type(other) == type(self)

class OptionBuilder(metaclass=abc.ABCMeta):
    """
    Base class of all option builders.
    All derived classes should implement
    
        - method :meth:`__len__`
        - method :meth:`build()`
    """

    @abc.abstractmethod
    def __len__(self):
        """
        Returns the number of options that would be returned by :meth:`build()`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def build(self):
        """
        Returns a list of options.
        """
        raise NotImplementedError