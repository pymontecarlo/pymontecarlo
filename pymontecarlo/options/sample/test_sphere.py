#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.sample.sphere import SphereSample, SphereSampleBuilder
from pymontecarlo.options.material import Material

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)

class TestSphereSample(TestCase):

    def setUp(self):
        super().setUp()

        self.s = SphereSample(COPPER, 123.456)

    def testskeleton(self):
        self.assertEqual(COPPER, self.s.material)
        self.assertAlmostEqual(123.456, self.s.diameter_m, 4)

    def testmaterials(self):
        self.assertEqual(1, len(self.s.materials))

    def test__eq__(self):
        s = SphereSample(COPPER, 123.456)
        self.assertEqual(s, self.s)

    def test__ne__(self):
        s = SphereSample(ZINC, 123.456)
        self.assertNotEqual(s, self.s)

        s = SphereSample(COPPER, 124.456)
        self.assertNotEqual(s, self.s)

class TestSphereSampleBuilder(TestCase):

    def testbuild(self):
        b = SphereSampleBuilder()
        b.add_material(COPPER)
        b.add_material(ZINC)
        b.add_diameter_m(1.0)

        samples = b.build()
        self.assertEqual(2, len(samples))
        self.assertEqual(2, len(b))

        for sample in samples:
            self.assertAlmostEqual(0.0, sample.tilt_rad, 4)
            self.assertAlmostEqual(0.0, sample.azimuth_rad, 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
