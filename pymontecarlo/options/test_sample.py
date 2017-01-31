#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math
import itertools

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.sample import \
    (_Sample, _SampleBuilder,
     Substrate, SubstrateBuilder,
     Inclusion, InclusionBuilder,
     HorizontalLayers,
     VerticalLayers,
     Sphere, SphereBuilder)
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)
GERMANIUM = Material.pure(32)

class SampleMock(_Sample):

    def __init__(self, tilt_rad, rotation_rad):
        super().__init__(tilt_rad, rotation_rad)

    @property
    def materials(self):
        return []

class SampleBuilderMock(_SampleBuilder):

    def build(self):
        samples = []
        for tilt_rad, rotation_rad in itertools.product(*self._get_combinations()):
            samples.append(SampleMock(tilt_rad, rotation_rad))
        return samples

class Test_Sample(TestCase):

    def setUp(self):
        super().setUp()

        self.s = SampleMock(1.1, 2.2)

    def testskeleton(self):
        self.assertAlmostEqual(1.1, self.s.tilt_rad, 4)
        self.assertAlmostEqual(2.2, self.s.rotation_rad, 4)
        self.assertAlmostEqual(math.degrees(1.1), self.s.tilt_deg, 4)
        self.assertAlmostEqual(math.degrees(2.2), self.s.rotation_deg, 4)

    def testget_materials(self):
        materials = self.s.materials
        self.assertEqual(0, len(materials))

class Test_SampleBuilder(TestCase):

    def testbuild(self):
        b = SampleBuilderMock()
        samples = b.build()
        self.assertEqual(1, len(samples))
        self.assertEqual(1, len(b))

        sample = samples[0]
        self.assertAlmostEqual(0.0, sample.tilt_rad, 4)
        self.assertAlmostEqual(0.0, sample.rotation_rad, 4)

    def testbuild2(self):
        b = SampleBuilderMock()
        b.add_tilt_rad(1.1)
        b.add_rotation_rad(2.2)

        samples = b.build()
        self.assertEqual(1, len(samples))

        sample = samples[0]
        self.assertAlmostEqual(1.1, sample.tilt_rad, 4)
        self.assertAlmostEqual(2.2, sample.rotation_rad, 4)

    def testbuild3(self):
        b = SampleBuilderMock()
        b.add_tilt_rad(1.1)
        b.add_tilt_rad(1.1)
        b.add_rotation_rad(2.2)
        b.add_rotation_rad(2.3)

        samples = b.build()
        self.assertEqual(2, len(samples))

class TestSubstrate(TestCase):

    def setUp(self):
        super().setUp()

        self.s = Substrate(COPPER)

    def testskeleton(self):
        self.assertEqual(COPPER, self.s.material)

    def testget_materials(self):
        materials = self.s.materials
        self.assertEqual(1, len(materials))

class TestSubstrateBuilder(TestCase):

    def testbuild(self):
        b = SubstrateBuilder()
        b.add_material(COPPER)
        b.add_material(ZINC)

        samples = b.build()
        self.assertEqual(2, len(samples))
        self.assertEqual(2, len(b))

        for sample in samples:
            self.assertAlmostEqual(0.0, sample.tilt_rad, 4)
            self.assertAlmostEqual(0.0, sample.rotation_rad, 4)

    def testbuild2(self):
        b = SubstrateBuilder()
        b.add_material(COPPER)
        b.add_material(ZINC)
        b.add_tilt_rad(0.0)

        samples = b.build()
        self.assertEqual(2, len(samples))
        self.assertEqual(2, len(b))

        for sample in samples:
            self.assertAlmostEqual(0.0, sample.tilt_rad, 4)
            self.assertAlmostEqual(0.0, sample.rotation_rad, 4)

    def testbuild3(self):
        b = SubstrateBuilder()
        b.add_material(COPPER)
        b.add_material(ZINC)
        b.add_tilt_rad(1.1)
        b.add_rotation_rad(2.2)

        samples = b.build()
        self.assertEqual(2, len(samples))
        self.assertEqual(2, len(b))

        for sample in samples:
            self.assertAlmostEqual(1.1, sample.tilt_rad, 4)
            self.assertAlmostEqual(2.2, sample.rotation_rad, 4)

    def testbuild4(self):
        b = SubstrateBuilder()
        b.add_material(COPPER)
        b.add_material(ZINC)
        b.add_tilt_rad(1.1)
        b.add_rotation_rad(2.2)
        b.add_rotation_rad(2.3)

        samples = b.build()
        self.assertEqual(4, len(samples))
        self.assertEqual(4, len(b))

    def testbuild5(self):
        b = SubstrateBuilder()
        b.add_tilt_rad(1.1)
        b.add_rotation_rad(2.2)
        b.add_rotation_rad(2.3)

        samples = b.build()
        self.assertEqual(0, len(samples))
        self.assertEqual(0, len(b))

class TestInclusion(TestCase):

    def setUp(self):
        super().setUp()

        self.s = Inclusion(COPPER, ZINC, 123.456)

    def testskeleton(self):
        self.assertEqual(COPPER, self.s.substrate_material)
        self.assertEqual(ZINC, self.s.inclusion_material)
        self.assertAlmostEqual(123.456, self.s.inclusion_diameter_m, 4)

    def testget_materials(self):
        materials = self.s.materials
        self.assertEqual(2, len(materials))

class TestInclusionBuilder(TestCase):

    def testbuild(self):
        b = InclusionBuilder()
        b.add_substrate_material(COPPER)
        b.add_substrate_material(ZINC)
        b.add_inclusion_material(GALLIUM)
        b.add_inclusion_diameter_m(1.0)
        b.add_inclusion_diameter_m(2.0)

        samples = b.build()
        self.assertEqual(4, len(samples))
        self.assertEqual(4, len(b))

        for sample in samples:
            self.assertAlmostEqual(0.0, sample.tilt_rad, 4)
            self.assertAlmostEqual(0.0, sample.rotation_rad, 4)

class TestHorizontalLayers(TestCase):

    def setUp(self):
        super().setUp()

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
        self.assertEqual(3, len(self.s1.materials))
        self.assertEqual(2, len(self.s2.materials))
        self.assertEqual(3, len(self.s3.materials))

class TestVerticalLayers(TestCase):

    def setUp(self):
        super().setUp()

        self.s1 = VerticalLayers(COPPER, ZINC)
        self.s1.add_layer(GALLIUM, 500.0)

        self.s2 = VerticalLayers(COPPER, ZINC)
        self.s2.add_layer(COPPER, 100.0)
        self.s2.add_layer(GERMANIUM, 200.0)

        self.s3 = VerticalLayers(COPPER, ZINC)
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

    def testget_materials(self):
        self.assertEqual(3, len(self.s1.materials))
        self.assertEqual(3, len(self.s2.materials))
        self.assertEqual(3, len(self.s3.materials))

class TestSphere(TestCase):

    def setUp(self):
        super().setUp()

        self.s = Sphere(COPPER, 123.456)

    def testskeleton(self):
        self.assertEqual(COPPER, self.s.material)
        self.assertAlmostEqual(123.456, self.s.diameter_m, 4)

    def testget_materials(self):
        self.assertEqual(1, len(self.s.materials))

class TestSphereBuilder(TestCase):

    def testbuild(self):
        b = SphereBuilder()
        b.add_material(COPPER)
        b.add_material(ZINC)
        b.add_diameter_m(1.0)

        samples = b.build()
        self.assertEqual(2, len(samples))
        self.assertEqual(2, len(b))

        for sample in samples:
            self.assertAlmostEqual(0.0, sample.tilt_rad, 4)
            self.assertAlmostEqual(0.0, sample.rotation_rad, 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
