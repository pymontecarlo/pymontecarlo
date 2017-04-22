#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.analysis.kratio import KRatioAnalysisHtmlHandler
from pymontecarlo.options.analysis.kratio import KRatioAnalysis

# Globals and constants variables.

class TestKRatioAnalysisHtmlHandler(TestCase):

    def testconvert(self):
        handler = KRatioAnalysisHtmlHandler()
        detector = self.create_basic_photondetector()
        analysis = KRatioAnalysis(detector)
        root = handler.convert(analysis)
        self.assertEqual(3, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
