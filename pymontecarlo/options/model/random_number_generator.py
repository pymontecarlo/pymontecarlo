"""
Random number generator models.
"""

__all__ = ["RandomNumberGeneratorModel"]

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import ModelBase

# Globals and constants variables.


class RandomNumberGeneratorModel(ModelBase):

    PRESS1996_RAND1 = ("Press et al. - rand1", "Press et al. (1966)")
    PRESS1996_RAND2 = ("Press et al. - rand2", "Press et al. (1966)")
    PRESS1996_RAND3 = ("Press et al. - rand3", "Press et al. (1966)")
    PRESS1996_RAND4 = ("Press et al. - rand4", "Press et al. (1966)")
    MERSENNE = ("Mersenne - Twister",)
    LAGGED_FIBONACCI = ("Lagged Fibonacci (Boost If607)",)
