#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.detector.photon.intensity import PhotonIntensityDetector

# Globals and constants variables.

class TestPhotonIntensityDetector(TestCase):

    def setUp(self):
        super().setUp()

        self.d = PhotonIntensityDetector(math.radians(35))

    def testskeleton(self):
        self.assertAlmostEqual(math.radians(35), self.d.elevation_rad, 4)
        self.assertAlmostEqual(35.0, self.d.elevation_deg, 4)

    def test__repr__(self):
        expected = '<PhotonIntensityDetector(35.0°)>'
        self.assertEqual(expected, repr(self.d))

    def test__eq__(self):
        d = PhotonIntensityDetector(math.radians(35))
        self.assertEqual(d, self.d)

    def test__ne__(self):
        d = PhotonIntensityDetector(math.radians(36))
        self.assertNotEqual(d, self.d)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
