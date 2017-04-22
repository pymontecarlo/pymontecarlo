#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.analysis.photonintensity import PhotonIntensityAnalysisHtmlHandler
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis

# Globals and constants variables.

class TestPhotonIntensityAnalysisHtmlHandler(TestCase):

    def testconvert(self):
        handler = PhotonIntensityAnalysisHtmlHandler()
        detector = self.create_basic_photondetector()
        analysis = PhotonIntensityAnalysis(detector)
        root = handler.convert(analysis)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
