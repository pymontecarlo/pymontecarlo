"""
Limit based on reaching uncertainty.
"""

# Standard library modules.

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.options.limit.base import Limit

# Globals and constants variables.

class UncertaintyLimit(Limit):

    def __init__(self, atomic_number, transition, detector, uncertainty):
        super().__init__()
        self.atomic_number = atomic_number
        self.transition = transition
        self.detector = detector
        self.uncertainty = uncertainty

    def __repr__(self):
        return '<{classname}({symbol} {iupac} <= {uncertainty}%)>' \
            .format(classname=self.__class__.__name__,
                    symbol=pyxray.element_symbol(self.atomic_number),
                    iupac=pyxray.transition_notation(self.transition, 'iupac'),
                    uncertainty=self.uncertainty * 100.0)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.atomic_number == other.atomic_number and \
            self.transition == other.transition and \
            self.detector == other.detector and \
            self.uncertainty == other.uncertainty

    def create_datarow(self):
        datarow = super().create_datarow()
        datarow['uncertainty X-ray transition'] = self.atomic_number, self.transition
        datarow.update(self.detector.parameters)
        datarow['uncertainty value'] = self.uncertainty
        return datarow

