#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.analysis.kratio import KRatioAnalysisSeriesHandler
from pymontecarlo.options.analysis.kratio import KRatioAnalysis

# Globals and constants variables.

class TestKRatioAnalysisSeriesHandler(TestCase):

    def testconvert(self):
        handler = KRatioAnalysisSeriesHandler()
        detector = self.create_basic_photondetector()
        analysis = KRatioAnalysis(detector)
        s = handler.convert(analysis)
        self.assertEqual(0, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
