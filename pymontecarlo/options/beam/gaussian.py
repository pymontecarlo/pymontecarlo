"""
Gaussian beam.
"""

__all__ = ["GaussianBeam", "GaussianBeamBuilder"]

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.beam.cylindrical import (
    CylindricalBeam,
    CylindricalBeamBuilder,
)
from pymontecarlo.options.particle import Particle

# Globals and constants variables.


class GaussianBeam(CylindricalBeam):
    def __init__(
        self, energy_eV, diameter_m, particle=Particle.ELECTRON, x0_m=0.0, y0_m=0.0
    ):
        """
        Creates a new Gaussian beam.
        
        A Gaussian beam is a two dimensional beam where the particles are
        distributed following a 2D-Gaussian distribution.

        :arg energy_eV: initial energy of the particle(s)
        :type energy_eV: :class:`float`
        
        :arg diameter_m: diameter of the beam.
            The diameter corresponds to the full width at half maximum (FWHM) of
            a two dimensional Gaussian distribution.
        :type diameter_m: :class:`float`
        
        :arg particle: type of particles [default: :data:`.ELECTRON`]
        :type particle: :mod:`.particle`
        
        :arg x0_m: initial x position where the beam first intersects the sample
        :type x0_m: :class:`float`
        
        :arg y0_m: initial y position where the beam first intersects the sample
        :type y0_m: :class:`float`
        """
        super().__init__(energy_eV, diameter_m, particle, x0_m, y0_m)


class GaussianBeamBuilder(CylindricalBeamBuilder):
    def _create_beam(self, energy_eV, diameter_m, particle, x0_m, y0_m):
        return GaussianBeam(energy_eV, diameter_m, particle, x0_m, y0_m)
