#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.sample.substrate import SubstrateSample, SubstrateSampleBuilder
from pymontecarlo.options.material import Material

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)

class TestSubstrateSample(TestCase):

    def setUp(self):
        super().setUp()

        self.s = SubstrateSample(COPPER)

    def testskeleton(self):
        self.assertEqual(COPPER, self.s.material)

    def testmaterials(self):
        materials = self.s.materials
        self.assertEqual(1, len(materials))

    def test__eq__(self):
        s = SubstrateSample(COPPER)
        self.assertEqual(s, self.s)

    def test__ne__(self):
        s = SubstrateSample(ZINC)
        self.assertNotEqual(s, self.s)

        s = SubstrateSample(COPPER, 1.1)
        self.assertNotEqual(s, self.s)

class TestSubstrateSampleBuilder(TestCase):

    def testbuild(self):
        b = SubstrateSampleBuilder()
        b.add_material(COPPER)
        b.add_material(ZINC)

        samples = b.build()
        self.assertEqual(2, len(samples))
        self.assertEqual(2, len(b))

        for sample in samples:
            self.assertAlmostEqual(0.0, sample.tilt_rad, 4)
            self.assertAlmostEqual(0.0, sample.azimuth_rad, 4)

    def testbuild2(self):
        b = SubstrateSampleBuilder()
        b.add_material(COPPER)
        b.add_material(ZINC)
        b.add_tilt_rad(0.0)

        samples = b.build()
        self.assertEqual(2, len(samples))
        self.assertEqual(2, len(b))

        for sample in samples:
            self.assertAlmostEqual(0.0, sample.tilt_rad, 4)
            self.assertAlmostEqual(0.0, sample.azimuth_rad, 4)

    def testbuild3(self):
        b = SubstrateSampleBuilder()
        b.add_material(COPPER)
        b.add_material(ZINC)
        b.add_tilt_rad(1.1)
        b.add_azimuth_rad(2.2)

        samples = b.build()
        self.assertEqual(2, len(samples))
        self.assertEqual(2, len(b))

        for sample in samples:
            self.assertAlmostEqual(1.1, sample.tilt_rad, 4)
            self.assertAlmostEqual(2.2, sample.azimuth_rad, 4)

    def testbuild4(self):
        b = SubstrateSampleBuilder()
        b.add_material(COPPER)
        b.add_material(ZINC)
        b.add_tilt_rad(1.1)
        b.add_azimuth_rad(2.2)
        b.add_azimuth_rad(2.3)

        samples = b.build()
        self.assertEqual(4, len(samples))
        self.assertEqual(4, len(b))

    def testbuild5(self):
        b = SubstrateSampleBuilder()
        b.add_tilt_rad(1.1)
        b.add_azimuth_rad(2.2)
        b.add_azimuth_rad(2.3)

        samples = b.build()
        self.assertEqual(0, len(samples))
        self.assertEqual(0, len(b))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
