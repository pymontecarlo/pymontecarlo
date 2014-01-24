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
    (PencilBeam, GaussianBeam, tilt_beam,
     convert_diameter_fwhm_to_sigma, convert_diameter_sigma_to_fwhm)
from pymontecarlo.options.particle import POSITRON

# Globals and constants variables.

class TestModule(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testtilt_beam(self):
        expecteds = [0.0, 1.0, 0.0]
        actuals = tilt_beam(math.pi / 2, axis='x', direction=(0, 0, -1))
        for expected, actual in zip(expecteds, actuals):
            self.assertAlmostEqual(expected, actual, 4)

        expecteds = [-1.0, 0.0, 0.0]
        actuals = tilt_beam(math.pi / 2, axis='y', direction=(0, 0, -1))
        for expected, actual in zip(expecteds, actuals):
            self.assertAlmostEqual(expected, actual, 4)

        expecteds = [0.0, 0.0, -1.0]
        actuals = tilt_beam(math.pi / 2, axis='z', direction=(0, 0, -1))
        for expected, actual in zip(expecteds, actuals):
            self.assertAlmostEqual(expected, actual, 4)

    def testconvert_diameter_fwhm_to_sigma(self):
        self.assertAlmostEqual(0.849321, convert_diameter_fwhm_to_sigma(1.0), 4)

    def testconvert_diameter_sigma_to_fwhm(self):
        self.assertAlmostEqual(1.0, convert_diameter_sigma_to_fwhm(0.849321), 4)

class TestPencilBeam(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.beam = PencilBeam(15e3, POSITRON,
                               (1.0, 2.0, 3.0), (4.0, 5.0, 6.0),
                               math.radians(3.5))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(POSITRON, self.beam.particle)

        self.assertAlmostEqual(15e3, self.beam.energy_eV, 4)
        self.assertAlmostEqual(15.0, self.beam.energy_keV, 4)

        self.assertAlmostEqual(1.0, self.beam.origin_m.x, 4)
        self.assertAlmostEqual(2.0, self.beam.origin_m.y, 4)
        self.assertAlmostEqual(3.0, self.beam.origin_m.z, 4)
        self.assertAlmostEqual(100.0, self.beam.origin_cm.x, 4)
        self.assertAlmostEqual(200.0, self.beam.origin_cm.y, 4)
        self.assertAlmostEqual(300.0, self.beam.origin_cm.z, 4)

        self.assertAlmostEqual(4.0, self.beam.direction.u, 4)
        self.assertAlmostEqual(5.0, self.beam.direction.v, 4)
        self.assertAlmostEqual(6.0, self.beam.direction.w, 4)

        self.assertAlmostEqual(0.81789, self.beam.direction_polar_rad, 4)
        self.assertAlmostEqual(0.89606, self.beam.direction_azimuth_rad, 4)

        self.assertAlmostEqual(math.radians(3.5), self.beam.aperture_rad, 4)

    def testdirection_polar_rad(self):
        beam = PencilBeam(15e3, direction=(0, 0, -1))
        self.assertAlmostEqual(3.14159, beam.direction_polar_rad, 4)

        beam = PencilBeam(15e3, direction=(0, 0, 1))
        self.assertAlmostEqual(0.0, beam.direction_polar_rad, 4)

        beam = PencilBeam(15e3, direction=[(0, 0, -1), (0, 0, 1)])
        self.assertAlmostEqual(3.14159, beam.direction_polar_rad[0], 4)
        self.assertAlmostEqual(0.0, beam.direction_polar_rad[1], 4)

    def testdirection_azimuth_rad(self):
        beam = PencilBeam(15e3, direction=(0, 0, -1))
        self.assertAlmostEqual(0.0, beam.direction_azimuth_rad, 4)

        beam = PencilBeam(15e3, direction=(1, 1, -1))
        self.assertAlmostEqual(0.78540, beam.direction_azimuth_rad, 4)

        beam = PencilBeam(15e3, direction=[(0, 0, -1), (1, 1, -1)])
        self.assertAlmostEqual(0.0, beam.direction_azimuth_rad[0], 4)
        self.assertAlmostEqual(0.78540, beam.direction_azimuth_rad[1], 4)

class TestGaussianBeam(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.beam = GaussianBeam(15e3, 123.456, POSITRON,
                                 (1.0, 2.0, 3.0), (4.0, 5.0, 6.0),
                                 math.radians(3.5))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(123.456, self.beam.diameter_m, 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
