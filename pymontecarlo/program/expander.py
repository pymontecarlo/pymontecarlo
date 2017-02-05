"""
Expander of detectors and limits
"""

# Standard library modules.
import abc
import itertools

# Third party modules.

# Local modules.

# Globals and constants variables.

def expand_to_single(objects):
    combinations = {}

    for object in objects:
        object_class = object.__class__
        combinations.setdefault(object_class, []).append(object)

    return list(itertools.product(*combinations.values()))

class Expander(metaclass=abc.ABCMeta):
    """
    Expands list of detectors and limits to match the simulation capabilities
    of a Monte Carlo program.
    """

    @abc.abstractmethod
    def expand_detectors(self, detectors):
        """
        Takes a :class:`list` of detectors and returns a :class:`list` of 
        :class:`tuple` where each tuple corresponds to the detectors for a
        single :class:`Options`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def expand_limits(self, limits):
        """
        Takes a :class:`list` of limits and returns a :class:`list` of 
        :class:`tuple` where each tuple corresponds to the limits for a
        single :class:`Options`.
        """
        raise NotImplementedError