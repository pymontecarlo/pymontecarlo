"""
Base figure.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.

# Globals and constants variables.

class Figure(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def draw(self, ax):
        """
        Draws a preview of the sample, beams and trajectories in a 
        matplotlib's :class:`Axes <matplotlib.axes.Axes>`.
        """
        raise NotImplementedError
