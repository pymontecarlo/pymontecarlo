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

from pymontecarlo.input.beam import \
    (PencilBeam, GaussianBeam, tilt_beam,
    convert_diameter_fwhm_to_sigma, convert_diameter_sigma_to_fwhm)
from pymontecarlo.input.particle import POSITRON

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
                               (1, 2, 3), (4, 5, 6), math.radians(3.5))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(POSITRON, self.beam.particle)

        self.assertAlmostEqual(15e3, self.beam.energy_eV, 4)
        self.assertAlmostEqual(15.0, self.beam.energy_keV, 4)

        self.assertAlmostEqual(1.0, self.beam.origin_m[0], 4)
        self.assertAlmostEqual(2.0, self.beam.origin_m[1], 4)
        self.assertAlmostEqual(3.0, self.beam.origin_m[2], 4)
        self.assertAlmostEqual(1.0, self.beam.origin_m.x, 4)
        self.assertAlmostEqual(2.0, self.beam.origin_m.y, 4)
        self.assertAlmostEqual(3.0, self.beam.origin_m.z, 4)
        self.assertAlmostEqual(100.0, self.beam.origin_cm[0], 4)
        self.assertAlmostEqual(200.0, self.beam.origin_cm[1], 4)
        self.assertAlmostEqual(300.0, self.beam.origin_cm[2], 4)

        self.assertAlmostEqual(4.0, self.beam.direction[0], 4)
        self.assertAlmostEqual(5.0, self.beam.direction[1], 4)
        self.assertAlmostEqual(6.0, self.beam.direction[2], 4)
        self.assertAlmostEqual(4.0, self.beam.direction.x, 4)
        self.assertAlmostEqual(5.0, self.beam.direction.y, 4)
        self.assertAlmostEqual(6.0, self.beam.direction.z, 4)

        self.assertAlmostEqual(0.81789, self.beam.direction_polar_rad, 4)
        self.assertAlmostEqual(0.89606, self.beam.direction_azimuth_rad, 4)

        self.assertAlmostEqual(math.radians(3.5), self.beam.aperture_rad, 4)

    def testdirection_polar_rad(self):
        beam = PencilBeam(15e3, direction=(0, 0, -1))
        self.assertAlmostEqual(3.14159, beam.direction_polar_rad, 4)

        beam = PencilBeam(15e3, direction=(0, 0, 1))
        self.assertAlmostEqual(0.0, beam.direction_polar_rad, 4)

    def testdirection_azimuth_rad(self):
        beam = PencilBeam(15e3, direction=(0, 0, -1))
        self.assertAlmostEqual(0.0, beam.direction_azimuth_rad, 4)

        beam = PencilBeam(15e3, direction=(1, 1, -1))
        self.assertAlmostEqual(0.78540, beam.direction_azimuth_rad, 4)

#    def testfrom_xml(self):
#        element = self.beam.to_xml()
#        beam = PencilBeam.from_xml(element)
#
#        self.assertEqual(POSITRON, beam.particle)
#
#        self.assertAlmostEqual(15e3, beam.energy_eV, 4)
#
#        self.assertAlmostEqual(1.0, beam.origin_m[0], 4)
#        self.assertAlmostEqual(2.0, beam.origin_m[1], 4)
#        self.assertAlmostEqual(3.0, beam.origin_m[2], 4)
#
#        self.assertAlmostEqual(4.0, beam.direction[0], 4)
#        self.assertAlmostEqual(5.0, beam.direction[1], 4)
#        self.assertAlmostEqual(6.0, beam.direction[2], 4)
#
#        self.assertAlmostEqual(math.radians(3.5), beam.aperture_rad, 4)
#
#    def testto_xml(self):
#        element = self.beam.to_xml()
#
#        self.assertEqual('positron', element.get('particle'))
#
#        self.assertAlmostEqual(15e3, float(element.get('energy')), 4)
#
#        child = element.find('origin')
#        self.assertAlmostEqual(1.0, float(child.get('x')), 4)
#        self.assertAlmostEqual(2.0, float(child.get('y')), 4)
#        self.assertAlmostEqual(3.0, float(child.get('z')), 4)
#
#        child = element.find('direction')
#        self.assertAlmostEqual(4.0, float(child.get('x')), 4)
#        self.assertAlmostEqual(5.0, float(child.get('y')), 4)
#        self.assertAlmostEqual(6.0, float(child.get('z')), 4)
#
#        self.assertAlmostEqual(math.radians(3.5), float(element.get('aperture')), 4)

class TestGaussianBeam(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.beam = GaussianBeam(15e3, 123.456, POSITRON,
                                 (1, 2, 3), (4, 5, 6), math.radians(3.5))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(123.456, self.beam.diameter_m, 4)
#
#    def testfrom_xml(self):
#        element = self.beam.to_xml()
#        beam = GaussianBeam.from_xml(element)
#
#        self.assertAlmostEqual(123.456, beam.diameter_m, 4)

#    def testto_xml(self):
#        element = self.beam.to_xml()
#
#        self.assertAlmostEqual(123.456, float(element.get('diameter')), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
