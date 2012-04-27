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

from pymontecarlo.input.geometry import \
    _Geometry, Substrate, Inclusion, MultiLayers, GrainBoundaries, Sphere
from pymontecarlo.input.material import pure, VACUUM
from pymontecarlo.input.body import Body, Layer

# Globals and constants variables.

class GeometryMock(_Geometry):

    def __init__(self, tilt, rotation):
        _Geometry.__init__(self, tilt, rotation)

        self.bodies = [Body(pure(29)), Body(VACUUM)]

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
        self.assertEqual(2, len(self.g.bodies))

    def testget_materials(self):
        materials = self.g.get_materials()
        self.assertEqual(2, len(materials))

    def test_indexify(self):
        self.g._indexify()
        self.assertEqual(0, VACUUM._index) #@UndefinedVariable
        self.assertEqual(1, self.g.bodies[0].material._index)

class TestSubstrate(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g = Substrate(pure(29))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.g.material))

    def testfrom_xml(self):
        self.g.tilt_rad = 1.1
        self.g.rotation_rad = 2.2
        element = self.g.to_xml()
        g = Substrate.from_xml(element)

        self.assertEqual('Copper', str(g.material))
        self.assertAlmostEqual(1.1, g.tilt_rad, 4)
        self.assertAlmostEqual(2.2, g.rotation_rad, 4)

    def testbody(self):
        self.assertEqual(self.g.material, self.g.body.material)

    def testget_bodies(self):
        self.assertEqual(1, len(self.g.get_bodies()))

    def testget_dimensions(self):
        dim = self.g.get_dimensions(self.g.body)
        self.assertEqual(float('-inf'), dim.xmin_m)
        self.assertEqual(float('inf'), dim.xmax_m)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertEqual(float('-inf'), dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

    def testto_xml(self):
        element = self.g.to_xml()

        self.assertEqual(1, len(list(element.find('materials'))))
        self.assertEqual(1, len(list(element.find('bodies'))))

        self.assertEqual(0, int(element.get('substrate')))

class TestInclusion(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g = Inclusion(pure(29), pure(30), 123.456)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.g.substrate_material))
        self.assertEqual('Zinc', str(self.g.inclusion_material))
        self.assertAlmostEqual(123.456, self.g.inclusion_diameter_m, 4)

    def testfrom_xml(self):
        self.g.tilt_rad = 1.1
        self.g.rotation_rad = 2.2
        element = self.g.to_xml()
        g = Inclusion.from_xml(element)

        self.assertEqual('Copper', str(g.substrate_material))
        self.assertEqual('Zinc', str(g.inclusion_material))
        self.assertAlmostEqual(123.456, g.inclusion_diameter_m, 4)

        self.assertAlmostEqual(1.1, g.tilt_rad, 4)
        self.assertAlmostEqual(2.2, g.rotation_rad, 4)

    def testsubstrate_body(self):
        self.assertEqual(self.g.substrate_material, self.g.substrate_body.material)

    def testinclusion_body(self):
        self.assertEqual(self.g.inclusion_material, self.g.inclusion_body.material)

    def testinclusion_diameter(self):
        self.assertAlmostEqual(123.456, self.g.inclusion_diameter_m, 4)

        self.assertRaises(ValueError, self.g.__setattr__, 'inclusion_diameter_m', -1)

    def testget_bodies(self):
        self.assertEqual(2, len(self.g.get_bodies()))

    def testget_dimensions(self):
        dim = self.g.get_dimensions(self.g.substrate_body)
        self.assertEqual(float('-inf'), dim.xmin_m)
        self.assertEqual(float('inf'), dim.xmax_m)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertEqual(float('-inf'), dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

        dim = self.g.get_dimensions(self.g.inclusion_body)
        self.assertAlmostEqual(-61.728, dim.xmin_m, 4)
        self.assertAlmostEqual(61.728, dim.xmax_m, 4)
        self.assertAlmostEqual(-61.728, dim.ymin_m, 4)
        self.assertAlmostEqual(61.728, dim.ymax_m, 4)
        self.assertAlmostEqual(-61.728, dim.zmin_m, 4)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

    def testto_xml(self):
        element = self.g.to_xml()

        self.assertEqual(2, len(list(element.find('materials'))))
        self.assertEqual(2, len(list(element.find('bodies'))))

        self.assertTrue(int(element.get('substrate')) in [0, 1])
        self.assertTrue(int(element.get('inclusion')) in [0, 1])

        self.assertAlmostEqual(123.456, float(element.get('diameter')), 4)

class TestMultiLayers(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g1 = MultiLayers(pure(29))
        self.g2 = MultiLayers(None)

        self.l1 = Layer(pure(30), 123.456)
        self.l2 = Layer(pure(31), 456.789)

        self.g1.layers.add(self.l1)
        self.g1.layers.add(self.l2)

        self.g2.layers.add(self.l1)
        self.g2.layers.add(self.l2)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        # Multi-layers 1
        self.assertTrue(self.g1.has_substrate())
        self.assertEqual('Copper', str(self.g1.substrate_material))

        self.assertEqual(2, len(self.g1.layers))
        self.assertEqual('Zinc', str(self.g1.layers[0].material))
        self.assertEqual('Gallium', str(self.g1.layers[1].material))

        # Multi-layers 2
        self.assertFalse(self.g2.has_substrate())

        self.assertEqual(2, len(self.g2.layers))
        self.assertEqual('Zinc', str(self.g2.layers[0].material))
        self.assertEqual('Gallium', str(self.g2.layers[1].material))

    def testfrom_xml(self):
        # Multi-layers 1
        self.g1.tilt_rad = 1.1
        self.g1.rotation_rad = 2.2
        element = self.g1.to_xml()
        g1 = MultiLayers.from_xml(element)

        self.assertTrue(g1.has_substrate())
        self.assertEqual('Copper', str(g1.substrate_material))

        self.assertEqual(2, len(g1.layers))
        self.assertEqual('Zinc', str(g1.layers[0].material))
        self.assertEqual('Gallium', str(g1.layers[1].material))

        self.assertAlmostEqual(1.1, g1.tilt_rad, 4)
        self.assertAlmostEqual(2.2, g1.rotation_rad, 4)

        # Multi-layers 2
        element = self.g2.to_xml()
        g2 = MultiLayers.from_xml(element)

        self.assertFalse(g2.has_substrate())

        self.assertEqual(2, len(g2.layers))
        self.assertEqual('Zinc', str(g2.layers[0].material))
        self.assertEqual('Gallium', str(g2.layers[1].material))

    def testsubstrate_material(self):
        self.g1.substrate_material = None
        self.assertFalse(self.g1.has_substrate())
        self.assertRaises(RuntimeError, self.g1.__getattribute__, 'substrate_material')

    def testsubstrate_body(self):
        self.assertEqual(self.g1.substrate_material, self.g1.substrate_body.material)

    def testget_bodies(self):
        self.assertEqual(3, len(self.g1.get_bodies()))
        self.assertEqual(2, len(self.g2.get_bodies()))

    def testget_dimensions(self):
        # Multi-layers 1
        dim = self.g1.get_dimensions(self.g1.substrate_body)
        self.assertEqual(float('-inf'), dim.xmin_m)
        self.assertEqual(float('inf'), dim.xmax_m)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertEqual(float('-inf'), dim.zmin_m)
        self.assertAlmostEqual(-580.245, dim.zmax_m, 4)

        dim = self.g1.get_dimensions(self.l1)
        self.assertEqual(float('-inf'), dim.xmin_m)
        self.assertEqual(float('inf'), dim.xmax_m)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertAlmostEqual(-123.456, dim.zmin_m, 4)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

        dim = self.g1.get_dimensions(self.l2)
        self.assertEqual(float('-inf'), dim.xmin_m)
        self.assertEqual(float('inf'), dim.xmax_m)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertAlmostEqual(-580.245, dim.zmin_m, 4)
        self.assertAlmostEqual(-123.456, dim.zmax_m, 4)

        # Multi-layers 2
        self.assertRaises(ValueError, self.g2.get_dimensions, self.g2.substrate_body)

        dim = self.g2.get_dimensions(self.l1)
        self.assertEqual(float('-inf'), dim.xmin_m)
        self.assertEqual(float('inf'), dim.xmax_m)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertAlmostEqual(-123.456, dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

        dim = self.g2.get_dimensions(self.l2)
        self.assertEqual(float('-inf'), dim.xmin_m)
        self.assertEqual(float('inf'), dim.xmax_m)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertAlmostEqual(-580.245, dim.zmin_m)
        self.assertAlmostEqual(-123.456, dim.zmax_m, 4)

    def testto_xml(self):
        # Multi-layers 1
        element = self.g1.to_xml()

        self.assertEqual(3, len(list(element.find('materials'))))
        self.assertEqual(3, len(list(element.find('bodies'))))

        layers = element.get('layers').split(',')
        self.assertEqual(2, len(layers))

        self.assertNotEqual(None, element.get('substrate'))

        # Multi-layers 2
        element = self.g2.to_xml()

        self.assertEqual(2, len(list(element.find('materials'))))
        self.assertEqual(2, len(list(element.find('bodies'))))

        layers = element.get('layers').split(',')
        self.assertEqual(2, len(layers))

        self.assertEqual(None, element.get('substrate'))

class TestGrainBoundaries(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g1 = GrainBoundaries(pure(29), pure(30))
        self.l1 = self.g1.add_layer(pure(31), 500.0)

        mat = pure(29)
        self.g2 = GrainBoundaries(mat, pure(30))
        self.l2 = self.g2.add_layer(mat, 100.0)
        self.l3 = self.g2.add_layer(pure(32), 200.0)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        # Grain boundaries 1
        self.assertEqual('Copper', str(self.g1.left_material))
        self.assertEqual('Zinc', str(self.g1.right_material))

        self.assertEqual(1, len(self.g1.layers))
        self.assertEqual('Gallium', str(self.g1.layers[0].material))

        # Grain boundaries 2
        self.assertEqual('Copper', str(self.g2.left_material))
        self.assertEqual('Zinc', str(self.g2.right_material))

        self.assertEqual(2, len(self.g2.layers))
        self.assertEqual('Copper', str(self.g2.layers[0].material))
        self.assertEqual('Germanium', str(self.g2.layers[1].material))

    def testfrom_xml(self):
        # Grain boundaries 1
        self.g1.tilt_rad = 1.1
        self.g1.rotation_rad = 2.2
        element = self.g1.to_xml()
        g = GrainBoundaries.from_xml(element)

        self.assertEqual('Copper', str(g.left_material))
        self.assertEqual('Zinc', str(g.right_material))

        self.assertEqual(1, len(g.layers))
        self.assertEqual('Gallium', str(g.layers[0].material))

        self.assertAlmostEqual(1.1, g.tilt_rad, 4)
        self.assertAlmostEqual(2.2, g.rotation_rad, 4)

        # Grain boundaries 2
        element = self.g2.to_xml()
        g = GrainBoundaries.from_xml(element)

        self.assertEqual('Copper', str(g.left_material))
        self.assertEqual('Zinc', str(g.right_material))

        self.assertEqual(2, len(g.layers))
        self.assertEqual('Copper', str(g.layers[0].material))
        self.assertEqual('Germanium', str(g.layers[1].material))

        self.assertAlmostEqual(0.0, g.tilt_rad, 4)
        self.assertAlmostEqual(0.0, g.rotation_rad, 4)

    def testleft_body(self):
        self.assertEqual(self.g1.left_material, self.g1.left_body.material)

    def testright_body(self):
        self.assertEqual(self.g1.right_material, self.g1.right_body.material)

    def testget_bodies(self):
        self.assertEqual(3, len(self.g1.get_bodies()))

    def testget_dimensions(self):
        # Grain boundaries 1
        dim = self.g1.get_dimensions(self.g1.left_body)
        self.assertEqual(float('-inf'), dim.xmin_m)
        self.assertAlmostEqual(-250.0, dim.xmax_m, 4)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertEqual(float('-inf'), dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

        dim = self.g1.get_dimensions(self.g1.right_body)
        self.assertAlmostEqual(250.0, dim.xmin_m, 4)
        self.assertEqual(float('inf'), dim.xmax_m)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertEqual(float('-inf'), dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

        dim = self.g1.get_dimensions(self.l1)
        self.assertAlmostEqual(-250.0, dim.xmin_m, 4)
        self.assertAlmostEqual(250.0, dim.xmax_m, 4)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertEqual(float('-inf'), dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

        # Grain boundaries 2
        dim = self.g2.get_dimensions(self.g2.left_body)
        self.assertEqual(float('-inf'), dim.xmin_m)
        self.assertAlmostEqual(-150.0, dim.xmax_m, 4)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertEqual(float('-inf'), dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

        dim = self.g2.get_dimensions(self.g2.right_body)
        self.assertAlmostEqual(150.0, dim.xmin_m, 4)
        self.assertEqual(float('inf'), dim.xmax_m)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertEqual(float('-inf'), dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

        dim = self.g2.get_dimensions(self.l2)
        self.assertAlmostEqual(-150.0, dim.xmin_m, 4)
        self.assertAlmostEqual(-50.0, dim.xmax_m, 4)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertEqual(float('-inf'), dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

        dim = self.g2.get_dimensions(self.l3)
        self.assertAlmostEqual(-50.0, dim.xmin_m, 4)
        self.assertAlmostEqual(150.0, dim.xmax_m, 4)
        self.assertEqual(float('-inf'), dim.ymin_m)
        self.assertEqual(float('inf'), dim.ymax_m)
        self.assertEqual(float('-inf'), dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

    def testto_xml(self):
        # Grain boundaries 1
        element = self.g1.to_xml()

        self.assertEqual(3, len(list(element.find('materials'))))
        self.assertEqual(3, len(list(element.find('bodies'))))

        layers = element.get('layers').split(',')
        self.assertEqual(1, len(layers))

        # Grain boundaries 2
        element = self.g2.to_xml()

        self.assertEqual(3, len(list(element.find('materials'))))
        self.assertEqual(4, len(list(element.find('bodies'))))

        layers = element.get('layers').split(',')
        self.assertEqual(2, len(layers))

class TestSphere(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.g = Sphere(pure(29), 123.456)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.g.material))
        self.assertAlmostEqual(123.456, self.g.diameter_m, 4)

    def testfrom_xml(self):
        self.g.tilt_rad = 1.1
        self.g.rotation_rad = 2.2
        element = self.g.to_xml()
        g = Sphere.from_xml(element)

        self.assertEqual('Copper', str(g.material))
        self.assertAlmostEqual(123.456, g.diameter_m, 4)

        self.assertAlmostEqual(1.1, g.tilt_rad, 4)
        self.assertAlmostEqual(2.2, g.rotation_rad, 4)

    def testsubstrate(self):
        self.assertEqual(self.g.material, self.g.body.material)

    def testdiameter_m(self):
        self.assertAlmostEqual(123.456, self.g.diameter_m, 4)

        self.assertRaises(ValueError, self.g.__setattr__, 'diameter_m', -1)

    def testget_bodies(self):
        self.assertEqual(1, len(self.g.get_bodies()))

    def testget_dimensions(self):
        dim = self.g.get_dimensions(self.g.body)
        self.assertEqual(-61.728, dim.xmin_m)
        self.assertEqual(61.728, dim.xmax_m)
        self.assertEqual(-61.728, dim.ymin_m)
        self.assertEqual(61.728, dim.ymax_m)
        self.assertEqual(-123.456, dim.zmin_m)
        self.assertAlmostEqual(0.0, dim.zmax_m, 4)

    def testto_xml(self):
        element = self.g.to_xml()

        self.assertEqual(1, len(list(element.find('materials'))))
        self.assertEqual(1, len(list(element.find('bodies'))))

        self.assertEqual(0, int(element.get('substrate')))

        self.assertAlmostEqual(123.456, float(element.get('diameter')), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
