#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.detector.photon import PhotonDetector, PhotonDetectorBuilder

# Globals and constants variables.

class TestPhotonDetector(TestCase):

    def setUp(self):
        super().setUp()

        self.d = PhotonDetector('det', math.radians(35), math.radians(90))

    def testskeleton(self):
        self.assertAlmostEqual(math.radians(35), self.d.elevation_rad, 4)
        self.assertAlmostEqual(35.0, self.d.elevation_deg, 4)

        self.assertAlmostEqual(math.radians(90), self.d.azimuth_rad, 4)
        self.assertAlmostEqual(90.0, self.d.azimuth_deg, 4)

    def test__repr__(self):
        expected = '<PhotonDetector(det, elevation=35.0°, azimuth=90.0°)>'
        self.assertEqual(expected, repr(self.d))

    def test__eq__(self):
        d = PhotonDetector('det', math.radians(35), math.radians(90))
        self.assertEqual(d, self.d)

    def test__ne__(self):
        d = PhotonDetector('det2', math.radians(35), math.radians(90))
        self.assertNotEqual(d, self.d)

        d = PhotonDetector(math.radians(36), math.radians(90))
        self.assertNotEqual(d, self.d)

        d = PhotonDetector(math.radians(35), math.radians(91))
        self.assertNotEqual(d, self.d)

class TestPhotonDetectorBuilder(TestCase):

    def testbuild(self):
        b = PhotonDetectorBuilder()
        b.add_azimuth_deg(0.0)
        self.assertEqual(0, len(b))
        self.assertEqual(0, len(b.build()))

    def testbuild2(self):
        b = PhotonDetectorBuilder()
        b.add_elevation_deg(1.1)
        self.assertEqual(1, len(b))
        self.assertEqual(1, len(b.build()))

    def testbuild3(self):
        b = PhotonDetectorBuilder()
        b.add_elevation_deg(1.1)
        b.add_elevation_deg(2.2)
        b.add_azimuth_deg(3.3)
        b.add_azimuth_deg(4.4)
        self.assertEqual(4, len(b))
        self.assertEqual(4, len(b.build()))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
