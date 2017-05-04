#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.detector.photon import PhotonDetectorHtmlHandler

# Globals and constants variables.

class TestPhotonDetectorHtmlHandler(TestCase):

    def testconvert(self):
        handler = PhotonDetectorHtmlHandler()
        detector = self.create_basic_photondetector()
        root = handler.convert(detector)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
