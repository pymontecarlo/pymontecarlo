#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample
from pymontecarlo.options.material import Material

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)
GERMANIUM = Material.pure(32)

class TestVerticalLayerSample(TestCase):

    def setUp(self):
        super().setUp()

        self.s1 = VerticalLayerSample(COPPER, ZINC)
        self.s1.add_layer(GALLIUM, 500.0)

        self.s2 = VerticalLayerSample(COPPER, ZINC)
        self.s2.add_layer(COPPER, 100.0)
        self.s2.add_layer(GERMANIUM, 200.0)

        self.s3 = VerticalLayerSample(COPPER, ZINC)
        self.s3.add_layer(GALLIUM, 500.0)
        self.s3.depth_m = 400.0

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

    def testmaterials(self):
        self.assertEqual(3, len(self.s1.materials))
        self.assertEqual(3, len(self.s2.materials))
        self.assertEqual(3, len(self.s3.materials))

    def test__eq__(self):
        s1 = VerticalLayerSample(COPPER, ZINC)
        s1.add_layer(GALLIUM, 500.0)
        self.assertEqual(s1, self.s1)

    def test__ne__(self):
        s1 = VerticalLayerSample(GERMANIUM, ZINC)
        s1.add_layer(GALLIUM, 500.0)
        self.assertNotEqual(s1, self.s1)

        s1 = VerticalLayerSample(COPPER, ZINC)
        self.assertNotEqual(s1, self.s1)

        s1 = VerticalLayerSample(COPPER, ZINC)
        s1.add_layer(GALLIUM, 501.0)
        self.assertNotEqual(s1, self.s1)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
