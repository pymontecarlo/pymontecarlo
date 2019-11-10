"""
Energy loss models.
"""

__all__ = ["EnergyLossModel"]

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import ModelBase

# Globals and constants variables.


class EnergyLossModel(ModelBase):

    JOY_LUO1989 = ("Joy and Luo 1989", "Joy and Luo (1989)")
    BETHE1930 = ("Bethe 1930", "Bethe H. Ann. Phys. (Leipzig) 1930; 5: 325")
    BETHE1960mod = ("Modified Bethe 1930", "Bethe H. Ann. Phys. (Leipzig) 1930; 5: 325")
    JOY_LUO_LOWNEY = ("Joy and Luo + Lowney",)
