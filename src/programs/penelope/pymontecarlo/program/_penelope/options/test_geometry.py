#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard and Hendrix Demers"
__email__ = "pypenelope-info@lists.sourceforge.net"
__version__ = "0.2.4"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard and Hendrix Demers"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.material import VACUUM
from pymontecarlo.program._penelope.options.geometry import \
    (Rotation, Shift, Scale, SurfaceImplicit, SurfaceReduced,
     xplane, zplane, cylinder, Module, PenelopeGeometry)
from pymontecarlo.program._penelope.options.material import Material, InteractionForcing

# Globals and constants variables.
from pymontecarlo.program._penelope.options.geometry import \
    SIDEPOINTER_NEGATIVE, SIDEPOINTER_POSITIVE
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.collision import HARD_BREMSSTRAHLUNG_EMISSION

class TestRotation(TestCase):
    GEOFILE = ['  OMEGA=(+1.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '  THETA=(+2.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '    PHI=(+3.000000000000000E+00,   0) DEG          (DEFAULT=0.0)']

    def setUp(self):
        TestCase.setUp(self)

        self.rotation = Rotation(radians(1.0), radians(2.0), radians(3.0))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(radians(1.0), self.rotation.omega_rad, 4)
        self.assertAlmostEqual(radians(2.0), self.rotation.theta_rad, 4)
        self.assertAlmostEqual(radians(3.0), self.rotation.phi_rad, 4)

    def testto_geo(self):
        lines = self.rotation.to_geo()
        self.assertEqual(3, len(lines))
        self.assertEqual(self.GEOFILE, lines)

class TestShift(TestCase):
    GEOFILE = ['X-SHIFT=(+1.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Y-SHIFT=(+2.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Z-SHIFT=(+3.000000000000000E+00,   0)              (DEFAULT=0.0)']

    def setUp(self):
        TestCase.setUp(self)

        self.shift = Shift(0.01, 0.02, 0.03)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(0.01, self.shift.x_m, 4)
        self.assertAlmostEqual(0.02, self.shift.y_m, 4)
        self.assertAlmostEqual(0.03, self.shift.z_m, 4)

    def testto_geo(self):
        lines = self.shift.to_geo()
        self.assertEqual(3, len(lines))
        self.assertEqual(self.GEOFILE, lines)

class TestScale(TestCase):
    GEOFILE = ['X-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               'Y-SCALE=(+2.000000000000000E+00,   0)              (DEFAULT=1.0)',
               'Z-SCALE=(+3.000000000000000E+00,   0)              (DEFAULT=1.0)']

    def setUp(self):
        TestCase.setUp(self)

        self.scale = Scale(1.0, 2.0, 3.0)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1.0, self.scale.x, 4)
        self.assertAlmostEqual(2.0, self.scale.y, 4)
        self.assertAlmostEqual(3.0, self.scale.z, 4)

    def testto_geo(self):
        lines = self.scale.to_geo()
        self.assertEqual(3, len(lines))
        self.assertEqual(self.GEOFILE, lines)

class TestSurfaceImplicit(TestCase):
    GEOFILE = ['SURFACE (   1) surface',
               'INDICES=( 0, 0, 0, 0, 0)',
               '    AXX=(+1.000000000000000E+03,   0)              (DEFAULT=0.0)',
               '    AXY=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '    AXZ=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '    AYY=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '    AYZ=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '    AZZ=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '     AX=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '     AY=(+1.000000000000000E+09,   0)              (DEFAULT=0.0)',
               '     AZ=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '     A0=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '1111111111111111111111111111111111111111111111111111111111111111',
               '  OMEGA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '  THETA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '    PHI=(+1.800000000000000E+02,   0) DEG          (DEFAULT=0.0)',
               'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Z-SHIFT=(-1.000000000000000E+05,   0)              (DEFAULT=0.0)']

    def setUp(self):
        TestCase.setUp(self)

        coefficients = (1e3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1e9, 0.0, 0.0)
        self.surface = SurfaceImplicit(coefficients, description='surface')
        self.surface.rotation.phi_rad = radians(180)
        self.surface.shift.z_m = -1e3
        self.surface._index = 0

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('surface', self.surface.description)
        self.assertAlmostEqual(radians(180), self.surface.rotation.phi_rad, 4)
        self.assertAlmostEqual(-1e3, self.surface.shift.z_m, 4)
        self.assertAlmostEqual(1e3, self.surface.coefficients['xx'], 4)
        self.assertAlmostEqual(0.0, self.surface.coefficients['xy'], 4)
        self.assertAlmostEqual(0.0, self.surface.coefficients['xz'], 4)
        self.assertAlmostEqual(0.0, self.surface.coefficients['yy'], 4)
        self.assertAlmostEqual(0.0, self.surface.coefficients['yz'], 4)
        self.assertAlmostEqual(0.0, self.surface.coefficients['zz'], 4)
        self.assertAlmostEqual(0.0, self.surface.coefficients['x'], 4)
        self.assertAlmostEqual(1e9, self.surface.coefficients['y'], 4)
        self.assertAlmostEqual(0.0, self.surface.coefficients['z'], 4)
        self.assertAlmostEqual(0.0, self.surface.coefficients['0'], 4)

    def testto_geo(self):
        lines = self.surface.to_geo()
        self.assertEqual(19, len(lines))
        self.assertEqual(self.GEOFILE, lines)

class TestSurfaceReduced(TestCase):
    GEOFILE = ['SURFACE (   1) surface',
               'INDICES=( 1, 1, 1, 0,-1)',
               'X-SCALE=(+3.000000000000000E+00,   0)              (DEFAULT=1.0)',
               'Y-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               'Z-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               '  OMEGA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '  THETA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '    PHI=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Z-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)']

    def setUp(self):
        TestCase.setUp(self)

        self.surface = SurfaceReduced((1, 1, 1, 0, -1), 'surface')
        self.surface.scale.x = 3.0
        self.surface._index = 0

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual((1, 1, 1, 0, -1), self.surface.indices)
        self.assertEqual('surface', self.surface.description)
        self.assertAlmostEqual(3.0, self.surface.scale.x, 4)

    def testto_geo(self):
        lines = self.surface.to_geo()
        self.assertEqual(11, len(lines))
        self.assertEqual(self.GEOFILE, lines)

class TestModule(TestCase):
    GEO1 = ['MODULE  (   1) Test',
            'MATERIAL(   1)',
            'SURFACE (   1), SIDE POINTER=(-1)',
            'SURFACE (   2), SIDE POINTER=( 1)',
            'MODULE  (   2)',
            '1111111111111111111111111111111111111111111111111111111111111111',
            '  OMEGA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
            '  THETA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
            '    PHI=(+1.800000000000000E+02,   0) DEG          (DEFAULT=0.0)',
            'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
            'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
            'Z-SHIFT=(-1.000000000000000E+05,   0)              (DEFAULT=0.0)']
    GEO2 = ['MODULE  (   2) ',
            'MATERIAL(   0)',
            '1111111111111111111111111111111111111111111111111111111111111111',
            '  OMEGA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
            '  THETA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
            '    PHI=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
            'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
            'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
            'Z-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)']

    def setUp(self):
        TestCase.setUp(self)

        intforce = InteractionForcing(ELECTRON, HARD_BREMSSTRAHLUNG_EMISSION, -4)
        mat1 = Material.pure(29, interaction_forcings=[intforce],
                             maximum_step_length_m=1e4)
        mat1._index = 1

        mat2 = VACUUM
        mat2._index = 0

        surface1 = SurfaceImplicit()
        surface1._index = 0

        surface2 = SurfaceImplicit()
        surface2._index = 1

        self.module2 = Module(None, mat2)
        self.module2._index = 1

        self.module1 = Module(None, mat1, 'Test')
        self.module1.add_surface(surface1, -1)
        self.module1.add_surface(surface2, 1)
        self.module1.add_module(self.module2)
        self.module1.rotation.phi_rad = radians(180)
        self.module1.shift.z_m = -1e3
        self.module1._index = 0

        self.materials_lookup = {0: mat2, 1: mat1}
        self.surfaces_lookup = {0: surface1, 1: surface2}
        self.modules_lookup = {0: self.module1, 1: self.module2}

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        # Module 1
        self.assertEqual('Copper', str(self.module1.material))
        self.assertAlmostEqual(1e4, self.module1.material.maximum_step_length_m, 4)
        self.assertEqual(1, len(self.module1.material.interaction_forcings))
        self.assertEqual('Test', self.module1.description)
        self.assertAlmostEqual(radians(180), self.module1.rotation.phi_rad, 4)
        self.assertAlmostEqual(-1e3, self.module1.shift.z_m, 4)
        self.assertEqual(2, len(self.module1.get_surfaces()))
        self.assertEqual(1, len(self.module1.get_modules()))

        # Module 2
        self.assertEqual(str(VACUUM), str(self.module2.material))
        self.assertEqual(0, len(self.module2.get_surfaces()))
        self.assertEqual(0, len(self.module2.get_modules()))

    def testto_geo(self):
        # Module 1
        lines = self.module1.to_geo()
        self.assertEqual(12, len(lines))
        self.assertEqual(self.GEO1, lines)

        # Module 2
        lines = self.module2.to_geo()
        self.assertEqual(9, len(lines))
        self.assertEqual(self.GEO2, lines)

class TestPenelopeGeometry(TestCase):
    GEOFILE = ['XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
               '       Test Geometry',
               '0000000000000000000000000000000000000000000000000000000000000000',
               'SURFACE (   1) Plane Z=0.00 m',
               'INDICES=( 0, 0, 0, 1, 0)',
               'X-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               'Y-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               'Z-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               '  OMEGA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '  THETA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '    PHI=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Z-SHIFT=(+1.000000000000000E-08,   0)              (DEFAULT=0.0)',
               '0000000000000000000000000000000000000000000000000000000000000000',
               'SURFACE (   2) Cylinder of radius 0.01 m along z-axis',
               'INDICES=( 1, 1, 0, 0,-1)',
               'X-SCALE=(+1.000000000000000E-02,   0)              (DEFAULT=1.0)',
               'Y-SCALE=(+1.000000000000000E-02,   0)              (DEFAULT=1.0)',
               'Z-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               '  OMEGA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '  THETA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '    PHI=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Z-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '0000000000000000000000000000000000000000000000000000000000000000',
               'SURFACE (   3) Plane Z=-0.00 m',
               'INDICES=( 0, 0, 0, 1, 0)',
               'X-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               'Y-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               'Z-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               '  OMEGA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '  THETA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '    PHI=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Z-SHIFT=(-1.000000000000000E-01,   0)              (DEFAULT=0.0)',
               '0000000000000000000000000000000000000000000000000000000000000000',
               'SURFACE (   4) Plane X=0.00 m',
               'INDICES=( 0, 0, 0, 1, 0)',
               'X-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               'Y-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               'Z-SCALE=(+1.000000000000000E+00,   0)              (DEFAULT=1.0)',
               '  OMEGA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '  THETA=(+9.000000000000000E+01,   0) DEG          (DEFAULT=0.0)',
               '    PHI=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Z-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '0000000000000000000000000000000000000000000000000000000000000000',
               'MODULE  (   1) ',
               'MATERIAL(   1)',
               'SURFACE (   1), SIDE POINTER=(-1)',
               'SURFACE (   2), SIDE POINTER=(-1)',
               'SURFACE (   3), SIDE POINTER=( 1)',
               'SURFACE (   4), SIDE POINTER=( 1)',
               '1111111111111111111111111111111111111111111111111111111111111111',
               '  OMEGA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '  THETA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '    PHI=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Z-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '0000000000000000000000000000000000000000000000000000000000000000',
               'MODULE  (   2) ',
               'MATERIAL(   2)',
               'SURFACE (   1), SIDE POINTER=(-1)',
               'SURFACE (   2), SIDE POINTER=(-1)',
               'SURFACE (   3), SIDE POINTER=( 1)',
               'MODULE  (   1)',
               '1111111111111111111111111111111111111111111111111111111111111111',
               '  OMEGA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '  THETA=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               '    PHI=(+0.000000000000000E+00,   0) DEG          (DEFAULT=0.0)',
               'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Z-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '0000000000000000000000000000000000000000000000000000000000000000',
               'MODULE  (   3) Extra module for rotation and tilt',
               'MATERIAL(   0)',
               'MODULE  (   2)',
               '1111111111111111111111111111111111111111111111111111111111111111',
               '  OMEGA=(+2.700000000000000E+02,   0) DEG          (DEFAULT=0.0)',
               '  THETA=(+4.500000000000000E+01,   0) DEG          (DEFAULT=0.0)',
               '    PHI=(+9.000000000000000E+01,   0) DEG          (DEFAULT=0.0)',
               'X-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Y-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               'Z-SHIFT=(+0.000000000000000E+00,   0)              (DEFAULT=0.0)',
               '0000000000000000000000000000000000000000000000000000000000000000',
               'END      0000000000000000000000000000000000000000000000000000000']

    def setUp(self):
        TestCase.setUp(self)

        self.geo = PenelopeGeometry('Test Geometry')

        surface1 = zplane(1e-10)
        surface2 = zplane(-1e-3)
        surface3 = cylinder(1e-2)
        surface4 = xplane(0.0)

        mat1 = Material.pure(29)
        self.module1 = Module(self.geo, mat1)
        self.module1.add_surface(surface1, SIDEPOINTER_NEGATIVE)
        self.module1.add_surface(surface2, SIDEPOINTER_POSITIVE)
        self.module1.add_surface(surface3, SIDEPOINTER_NEGATIVE)
        self.module1.add_surface(surface4, SIDEPOINTER_POSITIVE)
        self.geo.modules.add(self.module1)

        mat2 = Material.pure(30)
        self.module2 = Module(self.geo, mat2)
        self.module2.add_surface(surface1, SIDEPOINTER_NEGATIVE)
        self.module2.add_surface(surface2, SIDEPOINTER_POSITIVE)
        self.module2.add_surface(surface3, SIDEPOINTER_NEGATIVE)
        self.module2.add_module(self.module1)
        self.geo.modules.add(self.module2)

        self.geo.tilt_rad = radians(45)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Test Geometry', self.geo.title)
        self.assertAlmostEqual(radians(45), self.geo.tilt_rad, 4)
        self.assertAlmostEqual(0.0, self.geo.rotation_rad, 4)
        self.assertEqual(2, len(self.geo.get_bodies()))
        self.assertEqual(2, len(self.geo.modules))
        self.assertEqual(4, len(self.geo.get_surfaces()))
        self.assertEqual(2, len(self.geo.get_materials()))

    def testto_geo(self):
        lines = self.geo.to_geo()
        self.assertEqual(self.GEOFILE[:3], lines[:3])
        self.assertEqual(self.GEOFILE[14], lines[14])
        self.assertEqual(self.GEOFILE[26], lines[26])
        self.assertEqual(self.GEOFILE[38], lines[38])
        self.assertEqual(self.GEOFILE[50], lines[50])
        self.assertEqual(self.GEOFILE[51], lines[51])
        self.assertEqual(self.GEOFILE[57:65], lines[57:65])
        self.assertEqual(self.GEOFILE[65], lines[65])
        self.assertEqual(self.GEOFILE[71:], lines[71:])

#        with open('/home/ppinard/vboxshare/test.geo', 'w') as f:
#            for line in lines:
#                f.write(line + "\n")
#
#        i = 0
#        for exp, act in zip(self.GEOFILE, lines):
#            print i, exp, act, exp == act
#            i += 1

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
