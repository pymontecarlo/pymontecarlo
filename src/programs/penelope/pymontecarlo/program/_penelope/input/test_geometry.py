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

from pymontecarlo.program._penelope.input.geometry import \
    (Rotation, Shift, Scale, SurfaceImplicit, SurfaceReduced, PenelopeGeometry,
     xplane, zplane, cylinder, Module)
from pymontecarlo.input.material import VACUUM
from pymontecarlo.program._penelope.input.material import pure
from pymontecarlo.program._penelope.input.interactionforcing import InteractionForcing

# Globals and constants variables.
from pymontecarlo.program._penelope.input.geometry import \
    SIDEPOINTER_NEGATIVE, SIDEPOINTER_POSITIVE
from pymontecarlo.input.particle import ELECTRON
from pymontecarlo.input.collision import HARD_BREMSSTRAHLUNG_EMISSION

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

#    def testto_xml(self):
#        element = self.rotation.to_xml()
#
#        self.assertAlmostEqual(radians(1.0), float(element.get('omega')), 4)
#        self.assertAlmostEqual(radians(2.0), float(element.get('theta')), 4)
#        self.assertAlmostEqual(radians(3.0), float(element.get('phi')), 4)
#
#    def testfrom_xml(self):
#        element = self.rotation.to_xml()
#        rotation = Rotation.from_xml(element)
#
#        self.assertAlmostEqual(radians(1.0), rotation.omega_rad, 4)
#        self.assertAlmostEqual(radians(2.0), rotation.theta_rad, 4)
#        self.assertAlmostEqual(radians(3.0), rotation.phi_rad, 4)

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

#    def testto_xml(self):
#        element = self.shift.to_xml()
#
#        self.assertAlmostEqual(0.01, float(element.get('x')), 4)
#        self.assertAlmostEqual(0.02, float(element.get('y')), 4)
#        self.assertAlmostEqual(0.03, float(element.get('z')), 4)
#
#    def testfrom_xml(self):
#        element = self.shift.to_xml()
#        shift = Shift.from_xml(element)
#
#        self.assertAlmostEqual(0.01, shift.x_m, 4)
#        self.assertAlmostEqual(0.02, shift.y_m, 4)
#        self.assertAlmostEqual(0.03, shift.z_m, 4)

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

#    def testto_xml(self):
#        element = self.scale.to_xml()
#
#        self.assertAlmostEqual(1.0, float(element.get('x')), 4)
#        self.assertAlmostEqual(2.0, float(element.get('y')), 4)
#        self.assertAlmostEqual(3.0, float(element.get('z')), 4)
#
#    def testfrom_xml(self):
#        element = self.scale.to_xml()
#        scale = Scale.from_xml(element)
#
#        self.assertAlmostEqual(1.0, scale.x, 4)
#        self.assertAlmostEqual(2.0, scale.y, 4)
#        self.assertAlmostEqual(3.0, scale.z, 4)

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

        self.surface = SurfaceImplicit(description='surface')
        self.surface.coefficients['xx'] = 1e3
        self.surface.coefficients['y'] = 1e9
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

#    def testto_xml(self):
#        element = self.surface.to_xml()
#
#        self.assertEqual(0, int(element.get('index')))
#        self.assertEqual('surface', element.get('description'))
#
#        self.assertAlmostEqual(1e3, float(element.get('xx')), 4)
#        self.assertAlmostEqual(0.0, float(element.get('xy')), 4)
#        self.assertAlmostEqual(0.0, float(element.get('xz')), 4)
#        self.assertAlmostEqual(0.0, float(element.get('yy')), 4)
#        self.assertAlmostEqual(0.0, float(element.get('yz')), 4)
#        self.assertAlmostEqual(0.0, float(element.get('zz')), 4)
#        self.assertAlmostEqual(0.0, float(element.get('x')), 4)
#        self.assertAlmostEqual(1e9, float(element.get('y')), 4)
#        self.assertAlmostEqual(0.0, float(element.get('z')), 4)
#        self.assertAlmostEqual(0.0, float(element.get('0')), 4)
#
#        child = list(element.find('rotation'))[0]
#        self.assertAlmostEqual(radians(180), float(child.get('phi')), 4)
#
#        child = list(element.find('shift'))[0]
#        self.assertAlmostEqual(-1e3, float(child.get('z')), 4)
#
#    def testfrom_xml(self):
#        element = self.surface.to_xml()
#        surface = SurfaceImplicit.from_xml(element)
#
#        self.assertEqual('surface', surface.description)
#        self.assertAlmostEqual(radians(180), surface.rotation.phi_rad, 4)
#        self.assertAlmostEqual(-1e3, surface.shift.z_m, 4)
#        self.assertAlmostEqual(1e3, surface.coefficients['xx'], 4)
#        self.assertAlmostEqual(0.0, surface.coefficients['xy'], 4)
#        self.assertAlmostEqual(0.0, surface.coefficients['xz'], 4)
#        self.assertAlmostEqual(0.0, surface.coefficients['yy'], 4)
#        self.assertAlmostEqual(0.0, surface.coefficients['yz'], 4)
#        self.assertAlmostEqual(0.0, surface.coefficients['zz'], 4)
#        self.assertAlmostEqual(0.0, surface.coefficients['x'], 4)
#        self.assertAlmostEqual(1e9, surface.coefficients['y'], 4)
#        self.assertAlmostEqual(0.0, surface.coefficients['z'], 4)
#        self.assertAlmostEqual(0.0, surface.coefficients['0'], 4)

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

#    def testto_xml(self):
#        element = self.surface.to_xml()
#
#        self.assertEqual(0, int(element.get('index')))
#        self.assertEqual('surface', element.get('description'))
#
#        self.assertEqual(1, int(element.get('a')))
#        self.assertEqual(1, int(element.get('b')))
#        self.assertEqual(1, int(element.get('c')))
#        self.assertEqual(0, int(element.get('d')))
#        self.assertEqual(-1, int(element.get('e')))
#
#    def testfrom_xml(self):
#        element = self.surface.to_xml()
#        surface = SurfaceReduced.from_xml(element)
#
#        self.assertEqual((1, 1, 1, 0, -1), surface.indices)
#        self.assertEqual('surface', surface.description)
#        self.assertAlmostEqual(3.0, surface.scale.x, 4)

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

        mat1 = pure(29)
        mat1._index = 1

        mat2 = VACUUM
        mat2._index = 0

        surface1 = SurfaceImplicit()
        surface1._index = 0

        surface2 = SurfaceImplicit()
        surface2._index = 1

        self.module2 = Module(mat2)
        self.module2.maximum_step_length_m = 1e4
        intforce = InteractionForcing(ELECTRON, HARD_BREMSSTRAHLUNG_EMISSION, -4)
        self.module2.interaction_forcings.add(intforce)
        self.module2._index = 1

        self.module1 = Module(mat1, 'Test')
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
        self.assertEqual('Test', self.module1.description)
        self.assertAlmostEqual(radians(180), self.module1.rotation.phi_rad, 4)
        self.assertAlmostEqual(-1e3, self.module1.shift.z_m, 4)
        self.assertEqual(2, len(self.module1.get_surfaces()))
        self.assertEqual(1, len(self.module1.get_modules()))

        # Module 2
        self.assertEqual(str(VACUUM), str(self.module2.material))
        self.assertEqual(0, len(self.module2.get_surfaces()))
        self.assertEqual(0, len(self.module2.get_modules()))
        self.assertAlmostEqual(1e4, self.module2.maximum_step_length_m, 4)
        self.assertEqual(1, len(self.module2.interaction_forcings))

#    def testto_xml(self):
#        # Module 1
#        element = self.module1.to_xml()
#
#        self.assertEqual(0, int(element.get('index')))
#        self.assertEqual('Test', element.get('description'))
#
#        child = element.find('material')
#        self.assertEqual(1, int(child.get('index')))
#
#        children = list(element.find('surfaces'))
#        self.assertEqual(2, len(children))
#
#        children = list(element.find('modules'))
#        self.assertEqual(1, len(children))
#
#        # Module 2
#        element = self.module2.to_xml()
#
#        self.assertEqual(1, int(element.get('index')))
#        self.assertEqual('', element.get('description'))
#        self.assertAlmostEqual(1e4, float(element.get('maximumStepLength')), 4)
#
#        child = element.find('material')
#        self.assertEqual(0, int(child.get('index')))
#
#        children = element.find('interactionForcings')
#        self.assertEqual(1, len(children))
#
#    def testfrom_xml(self):
#        # Module 1
#        element = self.module1.to_xml()
#        module = Module.from_xml(element, self.materials_lookup,
#                                 self.surfaces_lookup, self.modules_lookup)
#
#        self.assertEqual('Copper', str(module.material))
#        self.assertEqual('Test', module.description)
#        self.assertAlmostEqual(radians(180), module.rotation.phi_rad, 4)
#        self.assertAlmostEqual(-1e3, module.shift.z_m, 4)
#        self.assertEqual(2, len(module.get_surfaces()))
#        self.assertEqual(1, len(module.get_modules()))
#
#        # Module 2
#        element = self.module2.to_xml()
#        module = Module.from_xml(element, self.materials_lookup,
#                                 self.surfaces_lookup, self.modules_lookup)
#
#        self.assertEqual(str(VACUUM), str(module.material))
#        self.assertEqual(0, len(module.get_surfaces()))
#        self.assertEqual(0, len(module.get_modules()))
#        self.assertAlmostEqual(1e4, module.maximum_step_length_m, 4)
#        self.assertEqual(1, len(module.interaction_forcings))

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

        mat1 = pure(29)
        self.module1 = Module(mat1)
        self.module1.add_surface(surface1, SIDEPOINTER_NEGATIVE)
        self.module1.add_surface(surface2, SIDEPOINTER_POSITIVE)
        self.module1.add_surface(surface3, SIDEPOINTER_NEGATIVE)
        self.module1.add_surface(surface4, SIDEPOINTER_POSITIVE)
        self.geo.modules.add(self.module1)

        mat2 = pure(30)
        self.module2 = Module(mat2)
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

#    def testfrom_xml(self):
#        element = self.geo.to_xml()
#        geo = PenelopeGeometry.from_xml(element)
#
#        self.assertEqual('Test Geometry', geo.title)
#        self.assertAlmostEqual(radians(45), geo.tilt_rad, 4)
#        self.assertAlmostEqual(0.0, geo.rotation_rad, 4)
#        self.assertEqual(2, len(geo.get_bodies()))
#        self.assertEqual(2, len(geo.modules))
#        self.assertEqual(4, len(geo.get_surfaces()))
#        self.assertEqual(2, len(geo.get_materials()))

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

#    def testto_xml(self):
#        element = self.geo.to_xml()
#
#        self.assertEqual('Test Geometry', element.get('title'))
#
#        self.assertAlmostEqual(radians(45), float(element.get('tilt')), 4)
#        self.assertAlmostEqual(0.0, float(element.get('rotation')), 4)
#
#        children = list(element.find('materials'))
#        self.assertEqual(2, len(children))
#
#        children = list(element.find('surfaces'))
#        self.assertEqual(4, len(children))
#
#        children = list(element.find('modules'))
#        self.assertEqual(2, len(children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
