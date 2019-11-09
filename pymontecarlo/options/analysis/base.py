"""
Base analysis.
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pymontecarlo.options.base import OptionBase, OptionBuilderBase
from pymontecarlo.util.human import camelcase_to_words

# Globals and constants variables.


class AnalysisBase(OptionBase):
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
        Calculates additional result(s) for this analysis.
        
        :arg simulation: simulation subjected to this analysis
        :type simulation: :class:`Simulation`
        
        :arg simulations: other simulations in the project
        :type simulations: :class`:list` of :class:`Simulation`
        
        :return: ``True`` if new results were added, ``False`` otherwise
        """
        return False

    @abc.abstractproperty
    def detector(self):
        """
        Returns the detector used by this analysis or ``None`` if no detector
        is necessary.
        """
        return None

    # region Document

    DESCRIPTION_DETECTOR = "detector"

    def convert_document(self, builder):
        super().convert_document(builder)

        builder.add_title(camelcase_to_words(self.__class__.__name__))


# endregion


class AnalysisBuilderBase(OptionBuilderBase):
    pass
