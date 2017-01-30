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
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.sample import \
    (_Sample, Substrate, Inclusion, HorizontalLayers, VerticalLayers,
     Sphere)
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)
GERMANIUM = Material.pure(32)

class SampleMock(_Sample):

    def __init__(self, tilt_rad, rotation_rad):
        super().__init__(tilt_rad, rotation_rad)

    def get_materials(self):
        return []

class Test_Sample(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.s = SampleMock(1.1, 2.2)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1.1, self.s.tilt_rad, 4)
        self.assertAlmostEqual(2.2, self.s.rotation_rad, 4)
        self.assertAlmostEqual(math.degrees(1.1), self.s.tilt_deg, 4)
        self.assertAlmostEqual(math.degrees(2.2), self.s.rotation_deg, 4)

    def testget_materials(self):
        materials = self.s.get_materials()
        self.assertEqual(0, len(materials))

class TestSubstrate(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.s = Substrate(COPPER)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(COPPER, self.s.material)

    def testget_materials(self):
        materials = self.s.get_materials()
        self.assertEqual(1, len(materials))

class TestInclusion(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.s = Inclusion(COPPER, ZINC, 123.456)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(COPPER, self.s.substrate_material)
        self.assertEqual(ZINC, self.s.inclusion_material)
        self.assertAlmostEqual(123.456, self.s.inclusion_diameter_m, 4)

    def testget_materials(self):
        materials = self.s.get_materials()
        self.assertEqual(2, len(materials))

class TestHorizontalLayers(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.s1 = HorizontalLayers(COPPER)
        self.s2 = HorizontalLayers(None) # No substrate
        self.s3 = HorizontalLayers(COPPER) # Empty layer

        self.s1.add_layer(ZINC, 123.456)
        self.s1.add_layer(GALLIUM, 456.789)

        self.s2.add_layer(ZINC, 123.456)
        self.s2.add_layer(GALLIUM, 456.789)

        self.s3.add_layer(ZINC, 123.456)
        self.s3.add_layer(GALLIUM, 456.789)
        self.s3.add_layer(VACUUM, 456.123)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        # Horizontal layers 1
        self.assertTrue(self.s1.has_substrate())
        self.assertEqual(COPPER, self.s1.substrate_material)

        self.assertEqual(2, len(self.s1.layers))
        self.assertEqual(ZINC, self.s1.layers[0].material)
        self.assertAlmostEqual(123.456, self.s1.layers[0].thickness_m, 4)
        self.assertEqual(GALLIUM, self.s1.layers[1].material)
        self.assertAlmostEqual(456.789, self.s1.layers[1].thickness_m, 4)

        # Horizontal layers 2
        self.assertFalse(self.s2.has_substrate())

        self.assertEqual(2, len(self.s2.layers))
        self.assertEqual(ZINC, self.s2.layers[0].material)
        self.assertAlmostEqual(123.456, self.s2.layers[0].thickness_m, 4)
        self.assertEqual(GALLIUM, self.s2.layers[1].material)
        self.assertAlmostEqual(456.789, self.s2.layers[1].thickness_m, 4)

        # Horizontal layers 3
        self.assertTrue(self.s3.has_substrate())
        self.assertEqual(COPPER, self.s3.substrate_material)

        self.assertEqual(3, len(self.s3.layers))
        self.assertEqual(ZINC, self.s3.layers[0].material)
        self.assertAlmostEqual(123.456, self.s3.layers[0].thickness_m, 4)
        self.assertEqual(GALLIUM, self.s3.layers[1].material)
        self.assertAlmostEqual(456.789, self.s3.layers[1].thickness_m, 4)
        self.assertEqual(VACUUM, self.s3.layers[2].material)
        self.assertAlmostEqual(456.123, self.s3.layers[2].thickness_m, 4)

    def testsubstrate(self):
        self.s1.substrate_material = VACUUM
        self.assertFalse(self.s1.has_substrate())

    def testget_materials(self):
        self.assertEqual(3, len(self.s1.get_materials()))
        self.assertEqual(3, len(self.s2.get_materials()))
        self.assertEqual(4, len(self.s3.get_materials()))

class TestVerticalLayers(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.s1 = VerticalLayers(COPPER, ZINC)
        self.s1.add_layer(GALLIUM, 500.0)

        self.s2 = VerticalLayers(COPPER, ZINC)
        self.s2.add_layer(COPPER, 100.0)
        self.s2.add_layer(GERMANIUM, 200.0)

        self.s3 = VerticalLayers(COPPER, ZINC)
        self.s3.add_layer(GALLIUM, 500.0)
        self.s3.depth_m = 400.0

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        # Vertical layers 1
        self.assertEqual(COPPER, self.s1.left_material)
        self.assertEqual(ZINC, self.s1.right_material)

        self.assertEqual(GALLIUM, self.s1.layers[0].material)
        self.assertAlmostEqual(500.0, self.s1.layers[0].thickness_m, 4)

        # Vertical layers 2
        self.assertEqual(COPPER, self.s2.left_material)
        self.assertEqual(ZINC, self.s2.right_material)

        self.assertEqual(2, len(self.s2.layers))
        self.assertEqual(COPPER, self.s2.layers[0].material)
        self.assertAlmostEqual(100.0, self.s2.layers[0].thickness_m, 4)
        self.assertAlmostEqual(200.0, self.s2.layers[1].thickness_m, 4)
        self.assertEqual(GERMANIUM, self.s2.layers[1].material)

        # Vertical layers 3
        self.assertEqual(COPPER, self.s3.left_material)
        self.assertEqual(ZINC, self.s3.right_material)

        self.assertEqual(GALLIUM, self.s3.layers[0].material)
        self.assertAlmostEqual(500.0, self.s3.layers[0].thickness_m, 4)

    def testget_materials(self):
        self.assertEqual(3, len(self.s1.get_materials()))
        self.assertEqual(4, len(self.s2.get_materials()))
        self.assertEqual(3, len(self.s3.get_materials()))

class TestSphere(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.s = Sphere(COPPER, 123.456)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(COPPER, self.s.material)
        self.assertAlmostEqual(123.456, self.s.diameter_m, 4)

    def testget_materials(self):
        self.assertEqual(1, len(self.s.get_materials()))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
