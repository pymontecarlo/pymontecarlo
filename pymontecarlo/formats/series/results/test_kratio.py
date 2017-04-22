#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.

from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.results.kratio import KRatioResultSeriesHandler
from pymontecarlo.options.analysis.kratio import KRatioAnalysis
from pymontecarlo.results.kratio import KRatioResultBuilder

# Globals and constants variables.

class TestKRatioResultSeriesHandler(TestCase):

    def testconvert(self):
        handler = KRatioResultSeriesHandler()
        analysis = KRatioAnalysis(self.create_basic_photondetector())
        b = KRatioResultBuilder(analysis)
        b.add_kratio((29, 'Ka1'), 2.0, 5.0)
        b.add_kratio((29, 'Ka'), 4.0, 5.0)
        result = b.build()
        s = handler.convert(result)
        self.assertEqual(4, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
