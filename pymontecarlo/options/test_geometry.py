#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.geometry import \
    (_Body, _Geometry, Substrate, Inclusion, HorizontalLayers, VerticalLayers,
     Sphere)
from pymontecarlo.options.material import Material, VACUUM
from pymontecarlo.util.parameter import expand

# Globals and constants variables.

class GeometryMock(_Geometry):

    def __init__(self, tilt, rotation):
        _Geometry.__init__(self, tilt, rotation)

        mat = Material.pure(29)
        self.bodies = [_Body(self, mat),
                       _Body(self, VACUUM),
                       _Body(self, mat)]

    def get_bodies(self):
        return self.bodies

class Test_Geometry(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g = GeometryMock(1.1, 2.2)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1.1, self.g.tilt_rad, 4)
        self.assertAlmostEqual(2.2, self.g.rotation_rad, 4)
        self.assertEqual(3, len(self.g.bodies))

    def testget_materials(self):
        materials = self.g.get_materials()
        self.assertEqual(1, len(materials))

class TestSubstrate(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g = Substrate(Material.pure(29))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.g.body.material))

    def testbody(self):
        self.assertEqual(float('-inf'), self.g.body.xmin_m)
        self.assertEqual(float('inf'), self.g.body.xmax_m)
        self.assertEqual(float('-inf'), self.g.body.ymin_m)
        self.assertEqual(float('inf'), self.g.body.ymax_m)
        self.assertEqual(float('-inf'), self.g.body.zmin_m)
        self.assertAlmostEqual(0.0, self.g.body.zmax_m, 4)

    def testmaterial(self):
        self.g.body.material = [Material.pure(14), Material.pure(15)]
        self.assertEqual(2, len(self.g.body.material))

    def testget_bodies(self):
        self.assertEqual(1, len(self.g.get_bodies()))

class TestInclusion(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g = Inclusion(Material.pure(29), Material.pure(30), 123.456)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.g.substrate.material))
        self.assertEqual('Zinc', str(self.g.inclusion.material))
        self.assertAlmostEqual(123.456, self.g.inclusion.diameter_m, 4)

    def testsubstrate(self):
        self.assertEqual(float('-inf'), self.g.substrate.xmin_m)
        self.assertEqual(float('inf'), self.g.substrate.xmax_m)
        self.assertEqual(float('-inf'), self.g.substrate.ymin_m)
        self.assertEqual(float('inf'), self.g.substrate.ymax_m)
        self.assertEqual(float('-inf'), self.g.substrate.zmin_m)
        self.assertAlmostEqual(0.0, self.g.substrate.zmax_m, 4)

    def testinclusion(self):
        # Dimensions
        self.assertAlmostEqual(-61.728, self.g.inclusion.xmin_m, 4)
        self.assertAlmostEqual(61.728, self.g.inclusion.xmax_m, 4)
        self.assertAlmostEqual(-61.728, self.g.inclusion.ymin_m, 4)
        self.assertAlmostEqual(61.728, self.g.inclusion.ymax_m, 4)
        self.assertAlmostEqual(-61.728, self.g.inclusion.zmin_m, 4)
        self.assertAlmostEqual(0.0, self.g.inclusion.zmax_m, 4)

        # Diameter
        self.assertAlmostEqual(123.456, self.g.inclusion.diameter_m, 4)
        self.assertRaises(ValueError, self.g.inclusion.__setattr__, 'diameter_m', -1)

    def testget_bodies(self):
        self.assertEqual(2, len(self.g.get_bodies()))

class TestHorizontalLayers(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g1 = HorizontalLayers(Material.pure(29))
        self.g2 = HorizontalLayers(None) # No substrate
        self.g3 = HorizontalLayers(Material.pure(29)) # Empty layer

        self.g1.add_layer(Material.pure(30), 123.456)
        self.g1.add_layer(Material.pure(31), 456.789)

        self.g2.add_layer(Material.pure(30), 123.456)
        self.g2.add_layer(Material.pure(31), 456.789)

        self.g3.add_layer(Material.pure(30), 123.456)
        self.g3.add_layer(Material.pure(31), 456.789)
        self.g3.add_layer(VACUUM, 456.123)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        # Horizontal layers 1
        self.assertTrue(self.g1.has_substrate())
        self.assertEqual('Copper', str(self.g1.substrate.material))

        self.assertEqual(2, len(self.g1.layers))
        self.assertEqual('Zinc', str(self.g1.layers[0].material))
        self.assertAlmostEqual(123.456, self.g1.layers[0].thickness_m, 4)
        self.assertEqual('Gallium', str(self.g1.layers[1].material))
        self.assertAlmostEqual(456.789, self.g1.layers[1].thickness_m, 4)

        # Horizontal layers 2
        self.assertFalse(self.g2.has_substrate())

        self.assertEqual(2, len(self.g2.layers))
        self.assertEqual('Zinc', str(self.g2.layers[0].material))
        self.assertAlmostEqual(123.456, self.g2.layers[0].thickness_m, 4)
        self.assertEqual('Gallium', str(self.g2.layers[1].material))
        self.assertAlmostEqual(456.789, self.g2.layers[1].thickness_m, 4)

        # Horizontal layers 3
        self.assertTrue(self.g3.has_substrate())
        self.assertEqual('Copper', str(self.g3.substrate.material))

        self.assertEqual(3, len(self.g3.layers))
        self.assertEqual('Zinc', str(self.g3.layers[0].material))
        self.assertAlmostEqual(123.456, self.g3.layers[0].thickness_m, 4)
        self.assertEqual('Gallium', str(self.g3.layers[1].material))
        self.assertAlmostEqual(456.789, self.g3.layers[1].thickness_m, 4)
        self.assertEqual('Vacuum', str(self.g3.layers[2].material))
        self.assertAlmostEqual(456.123, self.g3.layers[2].thickness_m, 4)

    def testsubstrate(self):
        self.g1.substrate.material = VACUUM
        self.assertFalse(self.g1.has_substrate())

        # Horizontal layers 1
        self.assertEqual(float('-inf'), self.g1.substrate.xmin_m)
        self.assertEqual(float('inf'), self.g1.substrate.xmax_m)
        self.assertEqual(float('-inf'), self.g1.substrate.ymin_m)
        self.assertEqual(float('inf'), self.g1.substrate.ymax_m)
        self.assertEqual(float('-inf'), self.g1.substrate.zmin_m)
        self.assertAlmostEqual(-580.245, self.g1.substrate.zmax_m, 4)

    def testlayers(self):
        # Horizontal layers 1
        self.assertEqual(float('-inf'), self.g1.layers[0].xmin_m)
        self.assertEqual(float('inf'), self.g1.layers[0].xmax_m)
        self.assertEqual(float('-inf'), self.g1.layers[0].ymin_m)
        self.assertEqual(float('inf'), self.g1.layers[0].ymax_m)
        self.assertAlmostEqual(-123.456, self.g1.layers[0].zmin_m, 4)
        self.assertAlmostEqual(0.0, self.g1.layers[0].zmax_m, 4)

        self.assertEqual(float('-inf'), self.g1.layers[1].xmin_m)
        self.assertEqual(float('inf'), self.g1.layers[1].xmax_m)
        self.assertEqual(float('-inf'), self.g1.layers[1].ymin_m)
        self.assertEqual(float('inf'), self.g1.layers[1].ymax_m)
        self.assertAlmostEqual(-580.245, self.g1.layers[1].zmin_m, 4)
        self.assertAlmostEqual(-123.456, self.g1.layers[1].zmax_m, 4)

        # Horizontal layers 2
        self.assertEqual(float('-inf'), self.g2.layers[0].xmin_m)
        self.assertEqual(float('inf'), self.g2.layers[0].xmax_m)
        self.assertEqual(float('-inf'), self.g2.layers[0].ymin_m)
        self.assertEqual(float('inf'), self.g2.layers[0].ymax_m)
        self.assertAlmostEqual(-123.456, self.g2.layers[0].zmin_m, 4)
        self.assertAlmostEqual(0.0, self.g2.layers[0].zmax_m, 4)

        self.assertEqual(float('-inf'), self.g2.layers[1].xmin_m)
        self.assertEqual(float('inf'), self.g2.layers[1].xmax_m)
        self.assertEqual(float('-inf'), self.g2.layers[1].ymin_m)
        self.assertEqual(float('inf'), self.g2.layers[1].ymax_m)
        self.assertAlmostEqual(-580.245, self.g2.layers[1].zmin_m, 4)
        self.assertAlmostEqual(-123.456, self.g2.layers[1].zmax_m, 4)

        # Horizontal layers 3
        self.assertEqual(float('-inf'), self.g3.layers[0].xmin_m)
        self.assertEqual(float('inf'), self.g3.layers[0].xmax_m)
        self.assertEqual(float('-inf'), self.g3.layers[0].ymin_m)
        self.assertEqual(float('inf'), self.g3.layers[0].ymax_m)
        self.assertAlmostEqual(-123.456, self.g3.layers[0].zmin_m, 4)
        self.assertAlmostEqual(0.0, self.g3.layers[0].zmax_m, 4)

        self.assertEqual(float('-inf'), self.g3.layers[1].xmin_m)
        self.assertEqual(float('inf'), self.g3.layers[1].xmax_m)
        self.assertEqual(float('-inf'), self.g3.layers[1].ymin_m)
        self.assertEqual(float('inf'), self.g3.layers[1].ymax_m)
        self.assertAlmostEqual(-580.245, self.g3.layers[1].zmin_m, 4)
        self.assertAlmostEqual(-123.456, self.g3.layers[1].zmax_m, 4)

        self.assertEqual(float('-inf'), self.g3.layers[2].xmin_m)
        self.assertEqual(float('inf'), self.g3.layers[2].xmax_m)
        self.assertEqual(float('-inf'), self.g3.layers[2].ymin_m)
        self.assertEqual(float('inf'), self.g3.layers[2].ymax_m)
        self.assertAlmostEqual(-1036.368, self.g3.layers[2].zmin_m, 4)
        self.assertAlmostEqual(-580.245, self.g3.layers[2].zmax_m, 4)

    def testget_bodies(self):
        self.assertEqual(3, len(self.g1.get_bodies()))
        self.assertEqual(2, len(self.g2.get_bodies()))
        self.assertEqual(4, len(self.g3.get_bodies()))

    def testget_materials(self):
        self.assertEqual(3, len(self.g1.get_materials()))
        self.assertEqual(2, len(self.g2.get_materials()))
        self.assertEqual(3, len(self.g3.get_materials()))

    def testexpand(self):
        self.assertEqual(1, len(expand(self.g1)))

        self.g1.add_layer(Material.pure(79), [1.0, 2.0])
        self.assertEqual(2, len(expand(self.g1)))

class TestVerticalLayers(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g1 = VerticalLayers(Material.pure(29), Material.pure(30))
        self.g1.add_layer(Material.pure(31), 500.0)

        self.g2 = VerticalLayers(Material.pure(29), Material.pure(30))
        self.g2.add_layer(Material.pure(29), 100.0)
        self.g2.add_layer(Material.pure(32), 200.0)

        self.g3 = VerticalLayers(Material.pure(29), Material.pure(30))
        self.g3.add_layer(Material.pure(31), 500.0)
        self.g3.depth_m = 400.0

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        # Vertical layers 1
        self.assertEqual('Copper', str(self.g1.left_substrate.material))
        self.assertEqual('Zinc', str(self.g1.right_substrate.material))

        self.assertEqual('Gallium', str(self.g1.layers[0].material))
        self.assertAlmostEqual(500.0, self.g1.layers[0].thickness_m, 4)

        # Vertical layers 2
        self.assertEqual('Copper', str(self.g2.left_substrate.material))
        self.assertEqual('Zinc', str(self.g2.right_substrate.material))

        self.assertEqual(2, len(self.g2.layers))
        self.assertEqual('Copper', str(self.g2.layers[0].material))
        self.assertAlmostEqual(100.0, self.g2.layers[0].thickness_m, 4)
        self.assertAlmostEqual(200.0, self.g2.layers[1].thickness_m, 4)
        self.assertEqual('Germanium', str(self.g2.layers[1].material))

        # Vertical layers 3
        self.assertEqual('Copper', str(self.g3.left_substrate.material))
        self.assertEqual('Zinc', str(self.g3.right_substrate.material))

        self.assertEqual('Gallium', str(self.g3.layers[0].material))
        self.assertAlmostEqual(500.0, self.g3.layers[0].thickness_m, 4)

    def testget_bodies(self):
        self.assertEqual(3, len(self.g1.get_bodies()))
        self.assertEqual(4, len(self.g2.get_bodies()))
        self.assertEqual(3, len(self.g3.get_bodies()))

    def testleft_substrate(self):
        # Vertical layers 1
        self.assertEqual(float('-inf'), self.g1.left_substrate.xmin_m)
        self.assertAlmostEqual(-250.0, self.g1.left_substrate.xmax_m, 4)
        self.assertEqual(float('-inf'), self.g1.left_substrate.ymin_m)
        self.assertEqual(float('inf'), self.g1.left_substrate.ymax_m)
        self.assertEqual(float('-inf'), self.g1.left_substrate.zmin_m)
        self.assertAlmostEqual(0.0, self.g1.left_substrate.zmax_m, 4)

        # Vertical layers 2
        self.assertEqual(float('-inf'), self.g2.left_substrate.xmin_m)
        self.assertAlmostEqual(-150.0, self.g2.left_substrate.xmax_m, 4)
        self.assertEqual(float('-inf'), self.g2.left_substrate.ymin_m)
        self.assertEqual(float('inf'), self.g2.left_substrate.ymax_m)
        self.assertEqual(float('-inf'), self.g2.left_substrate.zmin_m)
        self.assertAlmostEqual(0.0, self.g2.left_substrate.zmax_m, 4)

        # Vertical layers 3
        self.assertEqual(float('-inf'), self.g3.left_substrate.xmin_m)
        self.assertAlmostEqual(-250.0, self.g3.left_substrate.xmax_m, 4)
        self.assertEqual(float('-inf'), self.g3.left_substrate.ymin_m)
        self.assertEqual(float('inf'), self.g3.left_substrate.ymax_m)
        self.assertAlmostEqual(-400.0, self.g3.left_substrate.zmin_m, 4)
        self.assertAlmostEqual(0.0, self.g3.left_substrate.zmax_m, 4)

    def testright_substrate(self):
        # Vertical layers 1
        self.assertAlmostEqual(250.0, self.g1.right_substrate.xmin_m, 4)
        self.assertEqual(float('inf'), self.g1.right_substrate.xmax_m)
        self.assertEqual(float('-inf'), self.g1.right_substrate.ymin_m)
        self.assertEqual(float('inf'), self.g1.right_substrate.ymax_m)
        self.assertEqual(float('-inf'), self.g1.right_substrate.zmin_m)
        self.assertAlmostEqual(0.0, self.g1.right_substrate.zmax_m, 4)

        # Vertical layers 2
        self.assertAlmostEqual(150.0, self.g2.right_substrate.xmin_m, 4)
        self.assertEqual(float('inf'), self.g2.right_substrate.xmax_m)
        self.assertEqual(float('-inf'), self.g2.right_substrate.ymin_m)
        self.assertEqual(float('inf'), self.g2.right_substrate.ymax_m)
        self.assertEqual(float('-inf'), self.g2.right_substrate.zmin_m)
        self.assertAlmostEqual(0.0, self.g2.right_substrate.zmax_m, 4)

        # Vertical layers 3
        self.assertAlmostEqual(250.0, self.g3.right_substrate.xmin_m, 4)
        self.assertEqual(float('inf'), self.g3.right_substrate.xmax_m)
        self.assertEqual(float('-inf'), self.g3.right_substrate.ymin_m)
        self.assertEqual(float('inf'), self.g3.right_substrate.ymax_m)
        self.assertAlmostEqual(-400.0, self.g3.right_substrate.zmin_m, 4)
        self.assertAlmostEqual(0.0, self.g3.right_substrate.zmax_m, 4)

    def testlayers(self):
        # Vertical layers 1
        self.assertAlmostEqual(-250.0, self.g1.layers[0].xmin_m, 4)
        self.assertAlmostEqual(250.0, self.g1.layers[0].xmax_m, 4)
        self.assertEqual(float('-inf'), self.g1.layers[0].ymin_m)
        self.assertEqual(float('inf'), self.g1.layers[0].ymax_m)
        self.assertEqual(float('-inf'), self.g1.layers[0].zmin_m)
        self.assertAlmostEqual(0.0, self.g1.layers[0].zmax_m, 4)

        # Vertical layers 2
        self.assertAlmostEqual(-150.0, self.g2.layers[0].xmin_m, 4)
        self.assertAlmostEqual(-50.0, self.g2.layers[0].xmax_m, 4)
        self.assertEqual(float('-inf'), self.g2.layers[0].ymin_m)
        self.assertEqual(float('inf'), self.g2.layers[0].ymax_m)
        self.assertEqual(float('-inf'), self.g2.layers[0].zmin_m)
        self.assertAlmostEqual(0.0, self.g2.layers[0].zmax_m, 4)

        self.assertAlmostEqual(-50.0, self.g2.layers[1].xmin_m, 4)
        self.assertAlmostEqual(150.0, self.g2.layers[1].xmax_m, 4)
        self.assertEqual(float('-inf'), self.g2.layers[1].ymin_m)
        self.assertEqual(float('inf'), self.g2.layers[1].ymax_m)
        self.assertEqual(float('-inf'), self.g2.layers[1].zmin_m)
        self.assertAlmostEqual(0.0, self.g2.layers[1].zmax_m, 4)

        # Vertical layers 3
        self.assertAlmostEqual(-250.0, self.g3.layers[0].xmin_m, 4)
        self.assertAlmostEqual(250.0, self.g3.layers[0].xmax_m, 4)
        self.assertEqual(float('-inf'), self.g3.layers[0].ymin_m)
        self.assertEqual(float('inf'), self.g3.layers[0].ymax_m)
        self.assertAlmostEqual(-400.0, self.g3.layers[0].zmin_m, 4)
        self.assertAlmostEqual(0.0, self.g3.layers[0].zmax_m, 4)

    def testexpand(self):
        self.assertEqual(1, len(expand(self.g1)))

        self.g1.add_layer(Material.pure(79), [1.0, 2.0])
        self.assertEqual(2, len(expand(self.g1)))

class TestSphere(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g = Sphere(Material.pure(29), 123.456)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.g.body.material))
        self.assertAlmostEqual(123.456, self.g.body.diameter_m, 4)

    def testbody(self):
        self.assertAlmostEqual(-61.728, self.g.body.xmin_m, 4)
        self.assertAlmostEqual(61.728, self.g.body.xmax_m, 4)
        self.assertAlmostEqual(-61.728, self.g.body.ymin_m, 4)
        self.assertAlmostEqual(61.728, self.g.body.ymax_m, 4)
        self.assertAlmostEqual(-123.456, self.g.body.zmin_m, 4)
        self.assertAlmostEqual(0.0, self.g.body.zmax_m, 4)

        self.assertAlmostEqual(123.456, self.g.body.diameter_m, 4)
        self.assertRaises(ValueError, setattr, self.g.body, 'diameter_m', -1)

    def testget_bodies(self):
        self.assertEqual(1, len(self.g.get_bodies()))

# # # #class TestCuboids2D(TestCase):
# # # #
# # # #    def setUp(self):
# # # #        TestCase.setUp(self)
# # # #
# # # #        self.g = Cuboids2D(3, 3, 10, 10)
# # # #        self.g.material[0, 0] = pure(29)
# # # #        self.g.material[-1, -1] = pure(79)
# # # #
# # # #    def tearDown(self):
# # # #        TestCase.tearDown(self)
# # # #
# # # #    def testskeleton(self):
# # # #        self.assertEqual('Copper', str(self.g.material[0, 0]))
# # # #        self.assertEqual('Gold', str(self.g.material[-1, -1]))
# # # #        self.assertEqual('Vacuum', str(self.g.material[1, 1]))
# # # #
# # # #        self.assertEqual(3, self.g.nx)
# # # #        self.assertEqual(3, self.g.ny)
# # # #
# # # #        self.assertAlmostEqual(10.0, self.g.xsize_m, 4)
# # # #        self.assertAlmostEqual(10.0, self.g.ysize_m, 4)
# # # #
# # # #    def testfrom_xml(self):
# # # #        self.g.tilt_rad = 1.1
# # # #        self.g.rotation_rad = 2.2
# # # #        element = self.g.to_xml()
# # # #        g = Cuboids2D.from_xml(element)
# # # #
# # # #        self.assertEqual('Copper', str(self.g.material[0, 0]))
# # # #        self.assertEqual('Gold', str(self.g.material[-1, -1]))
# # # #        self.assertEqual('Vacuum', str(self.g.material[1, 1]))
# # # #
# # # #        self.assertAlmostEqual(10.0, self.g.xsize_m, 4)
# # # #        self.assertAlmostEqual(10.0, self.g.ysize_m, 4)
# # # #
# # # #        self.assertAlmostEqual(1.1, g.tilt_rad, 4)
# # # #        self.assertAlmostEqual(2.2, g.rotation_rad, 4)
# # # #
# # # #    def testbody(self):
# # # #        self.assertEqual('Copper', str(self.g.body[0, 0].material))
# # # #        self.assertEqual('Gold', str(self.g.body[-1, -1].material))
# # # #        self.assertEqual('Vacuum', str(self.g.body[1, 1].material))
# # # #
# # # #        self.assertRaises(IndexError, self.g.body.__getitem__, (2, 2))
# # # #
# # # #    def testmaterial(self):
# # # #        self.assertEqual('Copper', str(self.g.material[0, 0]))
# # # #        self.assertEqual('Gold', str(self.g.material[-1, -1]))
# # # #        self.assertEqual('Vacuum', str(self.g.material[1, 1]))
# # # #
# # # #        self.assertRaises(IndexError, self.g.material.__getitem__, (2, 2))
# # # #
# # # #    def testget_bodies(self):
# # # #        self.assertEqual(9, len(self.g.get_bodies()))
# # # #
# # # #    def testget_dimensions(self):
# # # #        dim = self.g.get_dimensions(self.g.body[0, 0])
# # # #        self.assertAlmostEqual(-5.0, dim.xmin_m, 4)
# # # #        self.assertAlmostEqual(5.0, dim.xmax_m, 4)
# # # #        self.assertAlmostEqual(-5.0, dim.ymin_m, 4)
# # # #        self.assertAlmostEqual(5.0, dim.ymax_m, 4)
# # # #        self.assertEqual(float('-inf'), dim.zmin_m)
# # # #        self.assertAlmostEqual(0.0, dim.zmax_m, 4)
# # # #
# # # #        dim = self.g.get_dimensions(self.g.body[-1, 0])
# # # #        self.assertAlmostEqual(-15.0, dim.xmin_m, 4)
# # # #        self.assertAlmostEqual(-5.0, dim.xmax_m, 4)
# # # #        self.assertAlmostEqual(-5.0, dim.ymin_m, 4)
# # # #        self.assertAlmostEqual(5.0, dim.ymax_m, 4)
# # # #        self.assertEqual(float('-inf'), dim.zmin_m)
# # # #        self.assertAlmostEqual(0.0, dim.zmax_m, 4)
# # # #
# # # #        dim = self.g.get_dimensions(self.g.body[1, 0])
# # # #        self.assertAlmostEqual(5.0, dim.xmin_m, 4)
# # # #        self.assertAlmostEqual(15.0, dim.xmax_m, 4)
# # # #        self.assertAlmostEqual(-5.0, dim.ymin_m, 4)
# # # #        self.assertAlmostEqual(5.0, dim.ymax_m, 4)
# # # #        self.assertEqual(float('-inf'), dim.zmin_m)
# # # #        self.assertAlmostEqual(0.0, dim.zmax_m, 4)
# # # #
# # # #        dim = self.g.get_dimensions(self.g.body[0, -1])
# # # #        self.assertAlmostEqual(-5.0, dim.xmin_m, 4)
# # # #        self.assertAlmostEqual(5.0, dim.xmax_m, 4)
# # # #        self.assertAlmostEqual(-15.0, dim.ymin_m, 4)
# # # #        self.assertAlmostEqual(-5.0, dim.ymax_m, 4)
# # # #        self.assertEqual(float('-inf'), dim.zmin_m)
# # # #        self.assertAlmostEqual(0.0, dim.zmax_m, 4)
# # # #
# # # #        dim = self.g.get_dimensions(self.g.body[0, 1])
# # # #        self.assertAlmostEqual(-5.0, dim.xmin_m, 4)
# # # #        self.assertAlmostEqual(5.0, dim.xmax_m, 4)
# # # #        self.assertAlmostEqual(5.0, dim.ymin_m, 4)
# # # #        self.assertAlmostEqual(15.0, dim.ymax_m, 4)
# # # #        self.assertEqual(float('-inf'), dim.zmin_m)
# # # #        self.assertAlmostEqual(0.0, dim.zmax_m, 4)
# # # #
# # # #    def testto_xml(self):
# # # #        element = self.g.to_xml()
# # # #
# # # #        self.assertEqual(2, len(list(element.find('materials'))))
# # # #        self.assertEqual(9, len(list(element.find('bodies'))))
# # # #        self.assertEqual(9, len(list(element.find('positions'))))
# # # #
# # # #        self.assertEqual(3, int(element.get('nx')))
# # # #        self.assertEqual(3, int(element.get('ny')))
# # # #        self.assertAlmostEqual(10.0, float(element.get('xsize')), 4)
# # # #        self.assertAlmostEqual(10.0, float(element.get('ysize')), 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
