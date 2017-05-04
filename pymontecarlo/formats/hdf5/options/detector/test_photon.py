#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.detector.photon import PhotonDetectorHDF5Handler
from pymontecarlo.options.detector.photon import PhotonDetector

# Globals and constants variables.

class TestPhotonDetectorHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = PhotonDetectorHDF5Handler()
        detector = PhotonDetector('det', math.radians(35), math.radians(45))
        detector2 = self.convert_parse_hdf5handler(handler, detector)
        self.assertEqual(detector2, detector)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
