#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.beam.gaussian import GaussianBeam
from pymontecarlo.options.particle import POSITRON, ELECTRON

# Globals and constants variables.

class TestPencilBeam(TestCase):

    def setUp(self):
        super().setUp()

        self.beam = GaussianBeam(15e3, 123.456, POSITRON, 1.0, 2.0, 0.1, 0.2)

    def testskeleton(self):
        self.assertEqual(POSITRON, self.beam.particle)

        self.assertAlmostEqual(15e3, self.beam.energy_eV, 4)
        self.assertAlmostEqual(15.0, self.beam.energy_keV, 4)

        self.assertAlmostEqual(123.456, self.beam.diameter_m, 4)

        self.assertAlmostEqual(1.0, self.beam.x0_m, 4)
        self.assertAlmostEqual(2.0, self.beam.y0_m, 4)

        self.assertAlmostEqual(0.1, self.beam.polar_rad, 4)
        self.assertAlmostEqual(math.degrees(0.1), self.beam.polar_deg, 4)

        self.assertAlmostEqual(0.2, self.beam.azimuth_rad, 4)
        self.assertAlmostEqual(math.degrees(0.2), self.beam.azimuth_deg, 4)

    def test__repr__(self):
        expected = '<GaussianBeam(positron, 15000 eV, 123.456 m, (1, 2) m, 0.1 rad, 0.2 rad)>'
        self.assertEqual(expected, repr(self.beam))

    def test__eq__(self):
        beam = GaussianBeam(15e3, 123.456, POSITRON, 1.0, 2.0, 0.1, 0.2)
        self.assertEqual(beam, self.beam)

    def test__ne__(self):
        beam = GaussianBeam(14e3, 123.456, POSITRON, 1.0, 2.0, 0.1, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = GaussianBeam(15e3, 124.456, POSITRON, 1.0, 2.0, 0.1, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = GaussianBeam(15e3, 123.456, ELECTRON, 1.0, 2.0, 0.1, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = GaussianBeam(15e3, 123.456, POSITRON, 1.1, 2.0, 0.1, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = GaussianBeam(15e3, 123.456, POSITRON, 1.0, 2.1, 0.1, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = GaussianBeam(15e3, 123.456, POSITRON, 1.0, 2.0, 0.11, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = GaussianBeam(15e3, 123.456, POSITRON, 1.0, 2.0, 0.1, 0.21)
        self.assertNotEqual(beam, self.beam)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
