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
from pymontecarlo.options.sample.base import _Sample, _SampleBuilder

# Globals and constants variables.

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

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
