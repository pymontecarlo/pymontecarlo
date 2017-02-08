#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.beam.gaussian import GaussianBeam, GaussianBeamBuilder
from pymontecarlo.options.particle import POSITRON, ELECTRON
from pymontecarlo.options.beam.base import Beam

# Globals and constants variables.

class TestGaussianBeam(TestCase):

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

        beam = Beam(15e3, POSITRON)
        self.assertNotEqual(beam, self.beam)

class TestGaussianBeamBuilder(TestCase):

    def testbuild(self):
        b = GaussianBeamBuilder()
        b.add_energy_eV(10e3)
        b.add_energy_keV(10) # Not added
        b.add_diameter_m(0.0)
        b.add_diameter_m(0.1)
        b.add_position(0.0, 0.0)
        b.add_position(0.0, 0.1)

        beams = b.build()
        self.assertEqual(4, len(beams))
        self.assertEqual(4, len(b))

        for beam in beams:
            self.assertEqual(ELECTRON, beam.particle)

    def testbuild_nodiameter(self):
        b = GaussianBeamBuilder()
        b.add_energy_eV(10e3)
        b.add_position(0.0, 0.0)
        b.add_position(0.0, 0.1)
        b.add_particle(ELECTRON)

        beams = b.build()
        self.assertEqual(0, len(beams))
        self.assertEqual(0, len(b))

    def testbuild_linescan(self):
        b = GaussianBeamBuilder()
        b.add_energy_eV(10e3)
        b.add_diameter_m(0.123)
        b.add_linescan_x(0.0, 5.0, 1.0, y0_m=0.456)

        beams = b.build()
        self.assertEqual(5, len(beams))
        self.assertEqual(5, len(b))

        for beam in beams:
            self.assertEqual(ELECTRON, beam.particle)
            self.assertAlmostEqual(0.123, beam.diameter_m, 4)
            self.assertAlmostEqual(0.456, beam.y0_m, 4)

    def testbuild_noposition(self):
        b = GaussianBeamBuilder()
        b.add_energy_eV(10e3)
        b.add_diameter_m(0.1)
        b.add_particle(ELECTRON)

        beams = b.build()
        self.assertEqual(1, len(beams))
        self.assertEqual(1, len(b))

        for beam in beams:
            self.assertAlmostEqual(0.0, beam.x0_m, 4)
            self.assertAlmostEqual(0.0, beam.y0_m, 4)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
