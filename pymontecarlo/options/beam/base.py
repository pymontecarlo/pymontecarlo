"""
Base classes for beams.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import MultiplierAttribute
from ..particle import ELECTRON

# Globals and constants variables.

class _Beam(object):
    """
    Base beam.
    """

    def __init__(self, energy_eV, particle=ELECTRON):
        """
        :arg energy_eV: initial energy of the particle(s)
        :type energy_eV: :class:`float`
        
        :arg particle: type of particles [default: :data:`.ELECTRON`]
        :type particle: :mod:`.particle`
        """
        self.energy_eV = energy_eV
        self.particle = particle

    def __eq__(self, other):
        return self.energy_eV == other.energy_eV and \
            self.particle == other.particle

    energy_keV = MultiplierAttribute('energy_eV', 1e-3)

def convert_diameter_fwhm_to_sigma(diameter):
    """
    Converts a beam diameter expressed as 2-sigma of a Gaussian distribution
    (radius = sigma) to a beam diameter expressed as the full with at half
    maximum (FWHM).

    :arg diameter: FWHM diameter.
    """
    # d_{FWHM} = 1.177411 (2\sigma)
    return diameter / 1.177411

def convert_diameter_sigma_to_fwhm(diameter):
    """
    Converts a beam diameter expressed as the full with at half maximum (FWHM)
    to a beam diameter expressed as 2-sigma of a Gaussian distribution
    (radius = sigma).

    :arg diameter: 2-sigma diameter diameter.
    """
    # d_{FWHM} = 1.177411 (2\sigma)
    return diameter * 1.177411
