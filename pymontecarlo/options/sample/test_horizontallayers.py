#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.sample.horizontallayers import \
    HorizontalLayerSample, HorizontalLayerSampleBuilder
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)

class TestHorizontalLayerSample(TestCase):

    def setUp(self):
        super().setUp()

        self.s1 = HorizontalLayerSample(COPPER)
        self.s2 = HorizontalLayerSample(None) # No substrate
        self.s3 = HorizontalLayerSample(COPPER) # Empty layer

        self.s1.add_layer(ZINC, 123.456)
        self.s1.add_layer(GALLIUM, 456.789)

        self.s2.add_layer(ZINC, 123.456)
        self.s2.add_layer(GALLIUM, 456.789)

        self.s3.add_layer(ZINC, 123.456)
        self.s3.add_layer(GALLIUM, 456.789)
        self.s3.add_layer(COPPER, 456.123)

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
        self.assertEqual(COPPER, self.s3.layers[2].material)
        self.assertAlmostEqual(456.123, self.s3.layers[2].thickness_m, 4)

    def testsubstrate(self):
        self.s1.substrate_material = VACUUM
        self.assertFalse(self.s1.has_substrate())

    def testmaterials(self):
        self.assertEqual(3, len(self.s1.materials))
        self.assertEqual(2, len(self.s2.materials))
        self.assertEqual(3, len(self.s3.materials))

    def testlayers_zpositions_m(self):
        # Horizontal layers 1
        zpositions_m = self.s1.layers_zpositions_m
        self.assertEqual(len(self.s1.layers), len(zpositions_m))

        zmin_m, zmax_m = zpositions_m[0]
        self.assertAlmostEqual(-123.456, zmin_m, 4)
        self.assertAlmostEqual(0.0, zmax_m, 4)

        zmin_m, zmax_m = zpositions_m[1]
        self.assertAlmostEqual(-123.456 - 456.789, zmin_m, 4)
        self.assertAlmostEqual(-123.456, zmax_m, 4)

        # Horizontal layers 2
        zpositions_m = self.s2.layers_zpositions_m
        self.assertEqual(len(self.s2.layers), len(zpositions_m))

        zmin_m, zmax_m = zpositions_m[0]
        self.assertAlmostEqual(-123.456, zmin_m, 4)
        self.assertAlmostEqual(0.0, zmax_m, 4)

        zmin_m, zmax_m = zpositions_m[1]
        self.assertAlmostEqual(-123.456 - 456.789, zmin_m, 4)
        self.assertAlmostEqual(-123.456, zmax_m, 4)

        # Horizontal layers 3
        zpositions_m = self.s3.layers_zpositions_m
        self.assertEqual(len(self.s3.layers), len(zpositions_m))

        zmin_m, zmax_m = zpositions_m[0]
        self.assertAlmostEqual(-123.456, zmin_m, 4)
        self.assertAlmostEqual(0.0, zmax_m, 4)

        zmin_m, zmax_m = zpositions_m[1]
        self.assertAlmostEqual(-123.456 - 456.789, zmin_m, 4)
        self.assertAlmostEqual(-123.456, zmax_m, 4)

        zmin_m, zmax_m = zpositions_m[2]
        self.assertAlmostEqual(-123.456 - 456.789 - 456.123, zmin_m, 4)
        self.assertAlmostEqual(-123.456 - 456.789, zmax_m, 4)

    def test__eq__(self):
        s1 = HorizontalLayerSample(COPPER)
        s1.add_layer(ZINC, 123.456)
        s1.add_layer(GALLIUM, 456.789)
        self.assertEqual(s1, self.s1)

    def test__ne__(self):
        s1 = HorizontalLayerSample(ZINC)
        s1.add_layer(ZINC, 123.456)
        s1.add_layer(GALLIUM, 456.789)
        self.assertNotEqual(s1, self.s1)

        s1 = HorizontalLayerSample(COPPER)
        s1.add_layer(GALLIUM, 456.789)
        self.assertNotEqual(s1, self.s1)

        s1 = HorizontalLayerSample(COPPER)
        s1.add_layer(ZINC, 124.456)
        s1.add_layer(GALLIUM, 456.789)
        self.assertNotEqual(s1, self.s1)

class TestHorizontalLayerSampleBuilder(TestCase):

    def testbuild(self):
        b = HorizontalLayerSampleBuilder()
        b.add_substrate_material(COPPER)
        bl = b.add_layer(ZINC, 10)
        bl.add_material(GALLIUM)

        samples = b.build()
        self.assertEqual(2, len(samples))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
