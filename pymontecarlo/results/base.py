"""
Base result.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.

class Result:

    @classmethod
    def getname(cls):
        name = cls.__name__
        if name.endswith('Result'):
            name = name[:-6]
        name = camelcase_to_words(name)
        return name.capitalize()

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
