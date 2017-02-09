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

    NAME = 'uncertainty limit'
    DESCRIPTION = 'Limits simulation to a certain uncertainty on the intensity of a certain X-ray transition.'

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

    @property
    def parameters(self):
        params = super().parameters
        params.add(('uncertainty X-ray transition', (self.atomic_number, self.transition)))
        params.update(self.detector.parameters)
        params.add(('uncertainty value', self.uncertainty))
        return params

