#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.analysis.photonintensity import PhotonIntensityAnalysisSeriesHandler
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis

# Globals and constants variables.

class TestPhotonIntensityAnalysisSeriesHandler(TestCase):

    def testconvert(self):
        handler = PhotonIntensityAnalysisSeriesHandler()
        detector = self.create_basic_photondetector()
        analysis = PhotonIntensityAnalysis(detector)
        s = handler.convert(analysis)
        self.assertEqual(0, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
