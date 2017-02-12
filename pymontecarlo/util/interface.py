"""
Interfaces.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.util.datarow import DataRow

# Globals and constants variables.



class DataRowCreator(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_datarow(self, **kwargs):
        return DataRow()
