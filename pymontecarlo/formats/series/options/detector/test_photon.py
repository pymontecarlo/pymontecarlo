#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.detector.photon import PhotonDetectorSeriesHandler

# Globals and constants variables.

class TestPhotonDetectorSeriesHandler(TestCase):

    def testconvert(self):
        handler = PhotonDetectorSeriesHandler()
        detector = self.create_basic_photondetector()
        s = handler.convert(detector)
        self.assertEqual(2, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
