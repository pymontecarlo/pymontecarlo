"""
Base classes for beams.
"""

# Standard library modules.
import functools
import operator
import math

# Third party modules.

# Local modules.
from pymontecarlo.util.cbook import MultiplierAttribute
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.base import Option, OptionBuilder

# Globals and constants variables.

class Beam(Option):
    """
    Base beam.
    """

    BEAM_ENERGY_TOLERANCE_eV = 1e-2 # 0.01 eV

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
            math.isclose(self.energy_eV, other.energy_eV, abs_tol=self.BEAM_ENERGY_TOLERANCE_eV) and \
            self.particle == other.particle

    def create_datarow(self, **kwargs):
        datarow = super().create_datarow(**kwargs)
        datarow.add('beam energy', self.energy_eV, 0.0, 'eV', self.BEAM_ENERGY_TOLERANCE_eV)
        return datarow

    energy_keV = MultiplierAttribute('energy_eV', 1e-3)

class BeamBuilder(OptionBuilder):

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
