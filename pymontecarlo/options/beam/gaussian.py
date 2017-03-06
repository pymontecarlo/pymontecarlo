"""
Gaussian beam.
"""

# Standard library modules.
import math
import itertools
import functools
import operator

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.options.beam.base import Beam, BeamBuilder
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.util.cbook import DegreesAttribute

# Globals and constants variables.

class GaussianBeam(Beam):

    DIAMETER_TOLERANCE_m = 1e-12 # 1 fm
    POSITION_TOLERANCE_m = 1e-12 # 1 pm
    POLAR_TOLERANCE_rad = math.radians(1e-3) # 0.001 deg
    AZIMUTH_TOLERANCE_rad = math.radians(1e-3) # 0.001 deg

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
        
        :arg x0_m: initial x position where the beam first intersects the sample
        :type x0_m: :class:`float`
        
        :arg y0_m: initial y position where the beam first intersects the sample
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
            math.isclose(self.diameter_m, other.diameter_m, abs_tol=self.DIAMETER_TOLERANCE_m) and \
            math.isclose(self.x0_m, other.x0_m, abs_tol=self.POSITION_TOLERANCE_m) and \
            math.isclose(self.y0_m, other.y0_m, abs_tol=self.POSITION_TOLERANCE_m) and \
            math.isclose(self.polar_rad, other.polar_rad, abs_tol=self.POLAR_TOLERANCE_rad) and \
            math.isclose(self.azimuth_rad, other.azimuth_rad, abs_tol=self.AZIMUTH_TOLERANCE_rad)

    def create_datarow(self, **kwargs):
        datarow = super().create_datarow(**kwargs)
        datarow.add('beam diameter', self.diameter_m, 0.0, 'm', self.DIAMETER_TOLERANCE_m)
        datarow.add('beam initial x position', self.x0_m, 0.0, 'm', self.POSITION_TOLERANCE_m)
        datarow.add('beam initial y position', self.x0_m, 0.0, 'm', self.POSITION_TOLERANCE_m)
        datarow.add('beam polar angle', self.polar_rad, 0.0, 'rad', self.POLAR_TOLERANCE_rad)
        datarow.add('beam azimuth angle', self.azimuth_rad, 0.0, 'rad', self.AZIMUTH_TOLERANCE_rad)
        return datarow

    polar_deg = DegreesAttribute('polar_rad')
    azimuth_deg = DegreesAttribute('azimuth_rad')

class GaussianBeamBuilder(BeamBuilder):

    def __init__(self):
        super().__init__()
        self.diameters_m = set()
        self.positions = set()

    def __len__(self):
        it = [super().__len__(),
              len(self.diameters_m),
              len(self.positions) or 1]
        return functools.reduce(operator.mul, it)

    def add_diameter_m(self, diameter_m):
        self.diameters_m.add(diameter_m)

    def add_position(self, x0_m, y0_m):
        self.positions.add((x0_m, y0_m))

    def add_linescan_x(self, x0_m, x1_m, xstep_m, y0_m=0.0):
        for x_m in np.arange(x0_m, x1_m, xstep_m):
            self.positions.add((x_m, y0_m))

    def build(self):
        particles = self.particles
        if not particles:
            particles = [ELECTRON]

        positions = self.positions
        if not positions:
            positions = [(0.0, 0.0)]

        product = itertools.product(self.energies_eV,
                                    self.diameters_m,
                                    particles,
                                    positions)

        beams = []
        for energy_eV, diameter_m, particle, (x0_m, y0_m) in product:
            beams.append(GaussianBeam(energy_eV, diameter_m, particle, x0_m, y0_m))

        return beams

