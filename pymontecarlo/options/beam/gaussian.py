"""
Gaussian beam.
"""

# Standard library modules.
import math

# Third party modules.

# Local modules.
from .base import _Beam
from ..particle import ELECTRON
from pymontecarlo.util.cbook import MultiplierAttribute

# Globals and constants variables.

class GaussianBeam(_Beam):

    def __init__(self, energy_eV, diameter_m, particle=ELECTRON,
                 x0_m=0.0, y0_m=0.0, polar_rad=math.pi, azimuth_rad=0.0):
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
        
        :arg x0_m: initial x position
        :type x0_m: :class:`float`
        
        :arg y0_m: initial y position
        :type y0_m: :class:`float`
        
        :arg polar_rad: angle of the beam with respect to the positive z-axis.
            By default, the beam points downwards, along the negative z-axis.
        :type polar_rad: :class:`float`
        
        :arg azimuth_rad: angle of the beam with respect to the positive x-axis 
            in the x-y plane. 
        :type azimuth_rad: :class:`float`
        """
        super().__init__(energy_eV, particle)

        self.diameter_m = diameter_m
        self.x0_m = x0_m
        self.y0_m = y0_m
        self.polar_rad = polar_rad
        self.azimuth_rad = azimuth_rad

    def __repr__(self):
        return '<{classname}({particle}, {energy_eV:g} eV, {diameter_m:g} m, ({x0_m:g}, {y0_m:g}) m, {polar_rad:g} rad, {azimuth_rad:g} rad)>' \
            .format(classname=self.__class__.__name__, **self.__dict__)

    def __eq__(self, other):
        return super().__eq__(other) and \
            self.diameter_m == other.diameter_m and \
            self.x0_m == other.x0_m and \
            self.y0_m == other.y0_m and \
            self.polar_rad == other.polar_rad and \
            self.azimuth_rad == other.azimuth_rad

    polar_deg = MultiplierAttribute('polar_rad', 180.0 / math.pi)
    azimuth_deg = MultiplierAttribute('azimuth_rad', 180.0 / math.pi)

