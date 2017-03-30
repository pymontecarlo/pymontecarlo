"""
Type of particles
"""

__all__ = ['Particle']

# Standard library modules.
import enum

# Third party modules.

# Local modules.

# Globals and constants variables.

class Particle(enum.Enum):
    ELECTRON = (-1, '#00549F')
    PHOTON = (0, '#FFD700')
    POSITRON = (1, '#FFAB60') # opposite color of ELECTRON

    def __init__(self, charge, color):
        self.charge = charge
        self.color = color

    def __str__(self):
        return self.name

