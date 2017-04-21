#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import itertools
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.sample.base import \
    Sample, SampleBuilder, LayeredSample, LayeredSampleBuilder
from pymontecarlo.options.material import Material

# Globals and constants variables.

class SampleMock(Sample):

    def __init__(self, tilt_rad, azimuth_rad):
        super().__init__(tilt_rad, azimuth_rad)

    @property
    def materials(self):
        return []

class SampleBuilderMock(SampleBuilder):

    def build(self):
        tilts_rad = self._calculate_tilt_combinations()
        rotations_rad = self._calculate_azimuth_combinations()

        samples = []
        for tilt_rad, azimuth_rad in itertools.product(tilts_rad, rotations_rad):
            samples.append(SampleMock(tilt_rad, azimuth_rad))
        return samples

class LayeredSampleBuilderMock(LayeredSampleBuilder):

    def build(self):
        layers_list = self._calculate_layer_combinations()
        tilts_rad = self._calculate_tilt_combinations()
        rotations_rad = self._calculate_azimuth_combinations()

        product = itertools.product(layers_list, tilts_rad, rotations_rad)

        samples = []
        for layers, tilt_rad, azimuth_rad in product:
            samples.append(LayeredSample(layers, tilt_rad, azimuth_rad))

        return samples

class TestSample(TestCase):

    def setUp(self):
        super().setUp()

        self.s = SampleMock(1.1, 2.2)

    def testskeleton(self):
        self.assertAlmostEqual(1.1, self.s.tilt_rad, 4)
        self.assertAlmostEqual(2.2, self.s.azimuth_rad, 4)
        self.assertAlmostEqual(math.degrees(1.1), self.s.tilt_deg, 4)
        self.assertAlmostEqual(math.degrees(2.2), self.s.azimuth_deg, 4)

    def testmaterials(self):
        materials = self.s.materials
        self.assertEqual(0, len(materials))

    def test__eq__(self):
        s = SampleMock(1.1, 2.2)
        self.assertEqual(s, self.s)

    def test__ne__(self):
        s = SampleMock(1.2, 2.2)
        self.assertNotEqual(s, self.s)

        s = SampleMock(1.1, 2.3)
        self.assertNotEqual(s, self.s)

class TestSampleBuilder(TestCase):

    def testbuild(self):
        b = SampleBuilderMock()
        samples = b.build()
        self.assertEqual(1, len(samples))
        self.assertEqual(1, len(b))

        sample = samples[0]
        self.assertAlmostEqual(0.0, sample.tilt_rad, 4)
        self.assertAlmostEqual(0.0, sample.azimuth_rad, 4)

    def testbuild2(self):
        b = SampleBuilderMock()
        b.add_tilt_rad(1.1)
        b.add_azimuth_rad(2.2)

        samples = b.build()
        self.assertEqual(1, len(samples))

        sample = samples[0]
        self.assertAlmostEqual(1.1, sample.tilt_rad, 4)
        self.assertAlmostEqual(2.2, sample.azimuth_rad, 4)

    def testbuild3(self):
        b = SampleBuilderMock()
        b.add_tilt_rad(1.1)
        b.add_tilt_rad(1.1)
        b.add_azimuth_rad(2.2)
        b.add_azimuth_rad(2.3)

        samples = b.build()
        self.assertEqual(2, len(samples))

class TestLayeredSampleBuilder(TestCase):

    def testbuild(self):
        b = LayeredSampleBuilderMock()
        b.add_layer(Material.pure(29), 10)
        b.add_layer(Material.pure(30), 20)

        samples = b.build()
        self.assertEqual(1, len(samples))

        sample = samples[0]
        self.assertEqual(2, len(sample.layers))

    def testbuild2(self):
        b = LayeredSampleBuilderMock()
        bl = b.add_layer(Material.pure(29), 10)
        bl.add_material(Material.pure(30))

        samples = b.build()
        self.assertEqual(2, len(samples))

        sample = samples[0]
        self.assertEqual(1, len(sample.layers))
        self.assertAlmostEqual(10, sample.layers[0].thickness_m, 4)

    def testbuild3(self):
        b = LayeredSampleBuilderMock()
        bl = b.add_layer(Material.pure(29), 10)
        bl.add_material(Material.pure(30))
        bl = b.add_layer(Material.pure(29), 20)
        bl.add_material(Material.pure(30))

        samples = b.build()
        self.assertEqual(4, len(samples))

        sample = samples[0]
        self.assertEqual(2, len(sample.layers))
        self.assertAlmostEqual(10, sample.layers[0].thickness_m, 4)
        self.assertAlmostEqual(20, sample.layers[1].thickness_m, 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
