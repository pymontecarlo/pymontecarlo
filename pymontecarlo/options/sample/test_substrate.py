#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.sample.substrate import Substrate, SubstrateBuilder
from pymontecarlo.options.material import Material

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)

class TestSubstrate(TestCase):

    def setUp(self):
        super().setUp()

        self.s = Substrate(COPPER)

    def testskeleton(self):
        self.assertEqual(COPPER, self.s.material)

    def testmaterials(self):
        materials = self.s.materials
        self.assertEqual(1, len(materials))

    def test__eq__(self):
        s = Substrate(COPPER)
        self.assertEqual(s, self.s)

    def test__ne__(self):
        s = Substrate(ZINC)
        self.assertNotEqual(s, self.s)

        s = Substrate(COPPER, 1.1)
        self.assertNotEqual(s, self.s)

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

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
