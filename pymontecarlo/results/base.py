"""
Base result.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class Result:

    def __init__(self, analysis):
        self.analysis = analysis

class ResultBuilder(metaclass=abc.ABCMeta):

    def __init__(self, analysis):
        self.analysis = analysis

    @abc.abstractmethod
    def build(self):
        """
        Returns one result.
        """
        raise NotImplementedError
