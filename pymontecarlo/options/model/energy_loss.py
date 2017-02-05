"""
Energy loss models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class EnergyLossModel(Model):

    @property
    def category(self):
        return 'energy loss'

JOY_LUO1989 = EnergyLossModel('Joy and Luo 1989', 'Joy and Luo (1989)')
BETHE1930 = EnergyLossModel("Bethe 1930", "Bethe H. Ann. Phys. (Leipzig) 1930; 5: 325")
BETHE1960mod = EnergyLossModel("Modified Bethe 1930", "Bethe H. Ann. Phys. (Leipzig) 1930; 5: 325")
JOY_LUO_LOWNEY = EnergyLossModel('Joy and Luo + Lowney',)
