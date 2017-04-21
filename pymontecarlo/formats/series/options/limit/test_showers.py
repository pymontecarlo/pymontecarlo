#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.limit.showers import ShowersLimitSeriesHandler
from pymontecarlo.options.limit.showers import ShowersLimit

# Globals and constants variables.

class TestShowersLimitSeriesHandler(TestCase):

    def testconvert(self):
        handler = ShowersLimitSeriesHandler()
        limit = ShowersLimit(123)
        s = handler.convert(limit)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
