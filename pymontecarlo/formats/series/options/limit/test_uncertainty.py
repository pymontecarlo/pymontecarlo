#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.limit.uncertainty import UncertaintyLimitSeriesHandler
from pymontecarlo.options.limit.uncertainty import UncertaintyLimit
from pymontecarlo.util.xrayline import XrayLine

# Globals and constants variables.

class TestUncertaintyLimitSeriesHandler(TestCase):

    def testconvert(self):
        handler = UncertaintyLimitSeriesHandler()
        detector = self.create_basic_photondetector()
        limit = UncertaintyLimit(XrayLine(13, 'Ka1'), detector, 0.02)
        s = handler.convert(limit)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
