#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.options import OptionsSeriesHandler

# Globals and constants variables.

class TestOptionsSeriesHandler(TestCase):

    def testconvert(self):
        handler = OptionsSeriesHandler()
        options = self.create_basic_options()
        s = handler.convert(options)
        self.assertEqual(14, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
