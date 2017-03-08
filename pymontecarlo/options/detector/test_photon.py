#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.

class TestPhotonIntensityDetector(TestCase):

    def setUp(self):
        super().setUp()

        self.d = PhotonDetector(math.radians(35), math.radians(90))

    def testskeleton(self):
        self.assertAlmostEqual(math.radians(35), self.d.elevation_rad, 4)
        self.assertAlmostEqual(35.0, self.d.elevation_deg, 4)

        self.assertAlmostEqual(math.radians(90), self.d.azimuth_rad, 4)
        self.assertAlmostEqual(90.0, self.d.azimuth_deg, 4)

    def test__repr__(self):
        expected = '<PhotonDetector(elevation=35.0°, azimuth=90.0°)>'
        self.assertEqual(expected, repr(self.d))

    def test__eq__(self):
        d = PhotonDetector(math.radians(35), math.radians(90))
        self.assertEqual(d, self.d)

    def test__ne__(self):
        d = PhotonDetector(math.radians(36), math.radians(90))
        self.assertNotEqual(d, self.d)

        d = PhotonDetector(math.radians(35), math.radians(91))
        self.assertNotEqual(d, self.d)

    def testcreate_datarow(self):
        self.assertEqual(2, len(self.d.create_datarow()))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
