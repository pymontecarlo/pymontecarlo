"""
Inelastic cross section models.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.model.base import Model

# Globals and constants variables.

class InelasticCrossSectionModel(Model):

    STERNHEIMER_LILJEQUIST1952 = ('Sternheimer-Liljequist generalised oscillator strength', 'Sternheimer, R. (1952). The density effect for the ionization loss in various materials. Phys. Rev., 88, 851-859. AND Liljequist, D. (1983). A simple calculation of inelastic mean free path and stopping power for 50 eV --50 keV electrons in solids. J. Phys. D: Appl. Phys., 16, 1567-1582.')
