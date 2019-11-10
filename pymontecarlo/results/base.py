"""
Base result.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.util.human import camelcase_to_words
from pymontecarlo.entity import EntityBase, EntityHDF5Mixin, EntitySeriesMixin

# Globals and constants variables.


class ResultBase(EntityBase, EntityHDF5Mixin, EntitySeriesMixin):
    @classmethod
    def getname(cls):
        name = cls.__name__
        if name.endswith("Result"):
            name = name[:-6]
        name = camelcase_to_words(name)
        return name.capitalize()

    def __init__(self, analysis):
        self.analysis = analysis

    # region HDF5

    ATTR_ANALYSIS = "analysis"

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_ANALYSIS, self.analysis)


# endregion


class ResultBuilderBase(metaclass=abc.ABCMeta):
    def __init__(self, analysis):
        self.analysis = analysis

    @abc.abstractmethod
    def build(self):
        """
        Returns one result.
        """
        raise NotImplementedError
