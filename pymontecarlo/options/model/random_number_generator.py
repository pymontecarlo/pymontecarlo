"""
Random number generator models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class RandomNumberGeneratorModel(Model):

    @property
    def category(self):
        return 'random number generator'

PRESS1996_RAND1 = RandomNumberGeneratorModel('Press et al. - rand1', 'Press et al. (1966)')
PRESS1996_RAND2 = RandomNumberGeneratorModel('Press et al. - rand2', 'Press et al. (1966)')
PRESS1996_RAND3 = RandomNumberGeneratorModel('Press et al. - rand3', 'Press et al. (1966)')
PRESS1996_RAND4 = RandomNumberGeneratorModel('Press et al. - rand4', 'Press et al. (1966)')
MERSENNE = RandomNumberGeneratorModel('Mersenne - Twister',)
LAGGED_FIBONACCI = RandomNumberGeneratorModel('Lagged Fibonacci (Boost If607)',)
