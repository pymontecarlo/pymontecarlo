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
    ELECTRON = -1
    PHOTON = 0
    POSITRON = 1

    def __str__(self):
        return self.name

    @property
    def charge(self):
        return self.value

