"""
Base classes for beams.
"""

# Standard library modules.
import functools
import operator

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import MultiplierAttribute, Builder
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.option import Option

# Globals and constants variables.

class Beam(Option):
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
        super().__init__()

        self.energy_eV = energy_eV
        self.particle = particle

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.energy_eV == other.energy_eV and \
            self.particle == other.particle

    energy_keV = MultiplierAttribute('energy_eV', 1e-3)

class BeamBuilder(Builder):

    def __init__(self):
        self.energies_eV = set()
        self.particles = set()

    def __len__(self):
        it = [len(self.energies_eV),
              len(self.particles) or 1]
        return functools.reduce(operator.mul, it)

    def add_energy_eV(self, energy_eV):
        self.energies_eV.add(energy_eV)

    def add_energy_keV(self, energy_keV):
        self.energies_eV.add(energy_keV * 1e3)

    def add_particle(self, particle):
        self.particles.add(particle)

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
