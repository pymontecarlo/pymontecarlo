"""
Base analysis.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.options.base import Option

# Globals and constants variables.

class Analysis(Option):

    @abc.abstractmethod
    def apply(self, options):
        """
        Returns other options necessary for this analysis.
        
        :arg options: options subjected to this analysis
        :type options: :class:`Options`
        
        :return: :class:`list` of other necessary options
        """
        return []

    @abc.abstractmethod
    def calculate(self, simulation, simulations):
        """
        Returns :class:`Result` for this analysis.
        
        :arg simulation: simulation subjected to this analysis
        :type simulation :class:`Simulation`
        
        :arg simulations: other simulations in the project
        :type simulations: :class`:list` of :class:`Simulation`
        
        :return: :class:`Result` of this analysis
        """
        return None

    @abc.abstractproperty
    def detectors(self):
        """
        Returns a :class:`tuple` of detectors used by this analysis.
        """
        return ()
