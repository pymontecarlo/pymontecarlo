"""
Limit based on the number of simulated particles.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.limit.base import Limit

# Globals and constants variables.

class ShowersLimit(Limit):

    def __init__(self, showers):
        super().__init__()
        self.showers = showers

    def __repr__(self):
        return '<{classname}({showers} trajectories)>' \
            .format(classname=self.__class__.__name__, **self.__dict__)

    def __eq__(self, other):
        return super().__eq__(other) and self.showers == other.showers

    @property
    def parameters(self):
        params = super().parameters
        params.add(('number of showers', self.showers))
        return params