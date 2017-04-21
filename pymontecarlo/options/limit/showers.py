"""
Limit based on the number of simulated particles.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.limit.base import Limit, LimitBuilder

# Globals and constants variables.

class ShowersLimit(Limit):

    def __init__(self, number_trajectories):
        super().__init__()
        self.number_trajectories = number_trajectories

    def __repr__(self):
        return '<{classname}({number_trajectories} trajectories)>' \
            .format(classname=self.__class__.__name__, **self.__dict__)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.number_trajectories == other.number_trajectories

class ShowersLimitBuilder(LimitBuilder):

    def __init__(self):
        super().__init__()
        self.numbers_trajectories = set()

    def __len__(self):
        return len(self.numbers_trajectories)

    def add_number_trajectories(self, number_trajectories):
        self.numbers_trajectories.add(number_trajectories)

    def build(self):
        return [ShowersLimit(n) for n in self.numbers_trajectories]
