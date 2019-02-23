""""""

__all__ = ['CylindricalBeam', 'CylindricalBeamBuilder']

# Standard library modules.
import functools
import operator
import itertools

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.options.beam.base import BeamBase, BeamBuilderBase
from pymontecarlo.options.particle import Particle
import pymontecarlo.options.base as base

# Globals and constants variables.

class CylindricalBeam(BeamBase):

    DIAMETER_TOLERANCE_m = 1e-12 # 1 fm
    POSITION_TOLERANCE_m = 1e-12 # 1 pm

    def __init__(self, energy_eV, diameter_m, particle=Particle.ELECTRON,
                 x0_m=0.0, y0_m=0.0):
        """
        Creates a new cylindrical beam.
        
        The initial position of the particle is sampled randomly
        within a circle of *diameter_m*, centered at (*x0_m*, *y0_m*) and 
        parallel to the z-axis.

        :arg energy_eV: initial energy of the particle(s)
        :type energy_eV: :class:`float`
        
        :arg diameter_m: diameter of the beam.
        :type diameter_m: :class:`float`
        
        :arg particle: type of particles [default: :data:`.ELECTRON`]
        :type particle: :mod:`.particle`
        
        :arg x0_m: initial x position where the beam first intersects the sample
        :type x0_m: :class:`float`
        
        :arg y0_m: initial y position where the beam first intersects the sample
        :type y0_m: :class:`float`
        """
        super().__init__(energy_eV, particle)

        self.diameter_m = diameter_m
        self.x0_m = x0_m
        self.y0_m = y0_m

    def __repr__(self):
        return '<{classname}({particle}, {energy_eV:g} eV, {diameter_m:g} m, ({x0_m:g}, {y0_m:g}) m)>' \
            .format(classname=self.__class__.__name__, **self.__dict__)

    def __eq__(self, other):
        return super().__eq__(other) and \
            base.isclose(self.diameter_m, other.diameter_m, abs_tol=self.DIAMETER_TOLERANCE_m) and \
            base.isclose(self.x0_m, other.x0_m, abs_tol=self.POSITION_TOLERANCE_m) and \
            base.isclose(self.y0_m, other.y0_m, abs_tol=self.POSITION_TOLERANCE_m)

#region HDF5

    ATTR_DIAMETER = 'diameter (m)'
    ATTR_X0 = 'x0 (m)'
    ATTR_Y0 = 'y0 (m)'

    @classmethod
    def parse_hdf5(cls, group):
        energy_eV = cls._parse_hdf5(group, cls.ATTR_ENERGY, float)
        diameter_m = cls._parse_hdf5(group, cls.ATTR_DIAMETER, float)
        particle = cls._parse_hdf5(group, cls.ATTR_PARTICLE, Particle)
        x0_m = cls._parse_hdf5(group, cls.ATTR_X0, float)
        y0_m = cls._parse_hdf5(group, cls.ATTR_Y0, float)
        return cls(energy_eV, diameter_m, particle, x0_m, y0_m)

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(group, self.ATTR_DIAMETER, self.diameter_m)
        self._convert_hdf5(group, self.ATTR_X0, self.x0_m)
        self._convert_hdf5(group, self.ATTR_Y0, self.y0_m)

#endregion

#region Series

    def convert_series(self, builder):
        super().convert_series(builder)
        builder.add_column('beam diameter', 'd0', self.diameter_m, 'm', self.DIAMETER_TOLERANCE_m)
        builder.add_column('beam initial x position', 'x0', self.x0_m, 'm', self.POSITION_TOLERANCE_m)
        builder.add_column('beam initial y position', 'y0', self.y0_m, 'm', self.POSITION_TOLERANCE_m)

#endregion

class CylindricalBeamBuilder(BeamBuilderBase):

    def __init__(self):
        super().__init__()
        self.diameters_m = set()
        self.positions = set()

    def __len__(self):
        it = [super().__len__(),
              len(self.diameters_m),
              len(self.positions)]
        return functools.reduce(operator.mul, it)

    def add_diameter_m(self, diameter_m):
        self.diameters_m.add(diameter_m)

    def add_position(self, x0_m, y0_m):
        self.positions.add((x0_m, y0_m))

    def add_linescan_x(self, x0_m, x1_m, xstep_m, y0_m=0.0):
        for x_m in np.arange(x0_m, x1_m, xstep_m):
            self.positions.add((x_m, y0_m))

    def _create_beam(self, energy_eV, diameter_m, particle, x0_m, y0_m):
        return CylindricalBeam(energy_eV, diameter_m, particle, x0_m, y0_m)

    def build(self):
        particles = self.particles
        if not particles:
            particles = [Particle.ELECTRON]

        product = itertools.product(self.energies_eV,
                                    self.diameters_m,
                                    particles,
                                    self.positions)

        beams = []
        for energy_eV, diameter_m, particle, (x0_m, y0_m) in product:
            beam = self._create_beam(energy_eV, diameter_m, particle, x0_m, y0_m)
            beams.append(beam)

        return beams
