#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.sample.inclusion import InclusionSample, InclusionSampleBuilder
from pymontecarlo.options.material import Material

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)

class TestInclusionSample(TestCase):

    def setUp(self):
        super().setUp()

        self.s = InclusionSample(COPPER, ZINC, 123.456)

    def testskeleton(self):
        self.assertEqual(COPPER, self.s.substrate_material)
        self.assertEqual(ZINC, self.s.inclusion_material)
        self.assertAlmostEqual(123.456, self.s.inclusion_diameter_m, 4)

    def testmaterials(self):
        materials = self.s.materials
        self.assertEqual(2, len(materials))

    def test__eq__(self):
        s = InclusionSample(COPPER, ZINC, 123.456)
        self.assertEqual(s, self.s)

    def test__ne__(self):
        s = InclusionSample(COPPER, GALLIUM, 123.456)
        self.assertNotEqual(s, self.s)

        s = InclusionSample(GALLIUM, ZINC, 123.456)
        self.assertNotEqual(s, self.s)

        s = InclusionSample(COPPER, ZINC, 124.456)
        self.assertNotEqual(s, self.s)

class TestInclusionSampleBuilder(TestCase):

    def testbuild(self):
        b = InclusionSampleBuilder()
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
            self.assertAlmostEqual(0.0, sample.azimuth_rad, 4)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
