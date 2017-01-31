#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.beam import \
    (PencilBeam, GaussianBeam,
     convert_diameter_fwhm_to_sigma, convert_diameter_sigma_to_fwhm)
from pymontecarlo.options.particle import POSITRON, ELECTRON

# Globals and constants variables.

class Testbeam(TestCase):

    def testconvert_diameter_fwhm_to_sigma(self):
        self.assertAlmostEqual(0.849321, convert_diameter_fwhm_to_sigma(1.0), 4)

    def testconvert_diameter_sigma_to_fwhm(self):
        self.assertAlmostEqual(1.0, convert_diameter_sigma_to_fwhm(0.849321), 4)

class TestPencilBeam(TestCase):

    def setUp(self):
        super().setUp()

        self.beam = PencilBeam(15e3, POSITRON, 1.0, 2.0, 0.1, 0.2)

    def testskeleton(self):
        self.assertEqual(POSITRON, self.beam.particle)

        self.assertAlmostEqual(15e3, self.beam.energy_eV, 4)
        self.assertAlmostEqual(15.0, self.beam.energy_keV, 4)

        self.assertAlmostEqual(1.0, self.beam.x0_m, 4)
        self.assertAlmostEqual(2.0, self.beam.y0_m, 4)

        self.assertAlmostEqual(0.1, self.beam.polar_rad, 4)
        self.assertAlmostEqual(math.degrees(0.1), self.beam.polar_deg, 4)

        self.assertAlmostEqual(0.2, self.beam.azimuth_rad, 4)
        self.assertAlmostEqual(math.degrees(0.2), self.beam.azimuth_deg, 4)

    def test__repr__(self):
        expected = '<PencilBeam(positron, 15000 eV, (1, 2) m, 0.1 rad, 0.2 rad)>'
        self.assertEqual(expected, repr(self.beam))

    def test__eq__(self):
        beam = PencilBeam(15e3, POSITRON, 1.0, 2.0, 0.1, 0.2)
        self.assertEqual(beam, self.beam)

    def test__ne__(self):
        beam = PencilBeam(14e3, POSITRON, 1.0, 2.0, 0.1, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = PencilBeam(15e3, ELECTRON, 1.0, 2.0, 0.1, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = PencilBeam(15e3, POSITRON, 1.1, 2.0, 0.1, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = PencilBeam(15e3, POSITRON, 1.0, 2.1, 0.1, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = PencilBeam(15e3, POSITRON, 1.0, 2.0, 0.11, 0.2)
        self.assertNotEqual(beam, self.beam)

        beam = PencilBeam(15e3, POSITRON, 1.0, 2.0, 0.1, 0.21)
        self.assertNotEqual(beam, self.beam)

class TestGaussianBeam(TestCase):

    def setUp(self):
        super().setUp()

        self.beam = GaussianBeam(15e3, 123.456, POSITRON, 1.0, 2.0, 0.1, 0.2)

    def testskeleton(self):
        self.assertEqual(POSITRON, self.beam.particle)

        self.assertAlmostEqual(15e3, self.beam.energy_eV, 4)
        self.assertAlmostEqual(15.0, self.beam.energy_keV, 4)

        self.assertAlmostEqual(1.0, self.beam.x0_m, 4)
        self.assertAlmostEqual(2.0, self.beam.y0_m, 4)

        self.assertAlmostEqual(0.1, self.beam.polar_rad, 4)
        self.assertAlmostEqual(math.degrees(0.1), self.beam.polar_deg, 4)

        self.assertAlmostEqual(0.2, self.beam.azimuth_rad, 4)
        self.assertAlmostEqual(math.degrees(0.2), self.beam.azimuth_deg, 4)

        self.assertAlmostEqual(123.456, self.beam.diameter_m, 4)

    def test__repr__(self):
        expected = '<GaussianBeam(positron, 15000 eV, 123.456 m, (1, 2) m, 0.1 rad, 0.2 rad)>'
        self.assertEqual(expected, repr(self.beam))

    def test__eq__(self):
        beam = GaussianBeam(15e3, 123.456, POSITRON, 1.0, 2.0, 0.1, 0.2)
        self.assertEqual(beam, self.beam)

    def test__ne__(self):
        beam = GaussianBeam(15e3, 124.456, POSITRON, 1.0, 2.0, 0.1, 0.2)
        self.assertNotEqual(beam, self.beam)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
