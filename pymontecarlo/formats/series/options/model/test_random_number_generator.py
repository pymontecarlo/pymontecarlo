#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.random_number_generator import RandomNumberGeneratorModelSeriesHandler
from pymontecarlo.options.model.random_number_generator import RandomNumberGeneratorModel

# Globals and constants variables.

class TestRandomNumberGeneratorModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = RandomNumberGeneratorModelSeriesHandler()
        model = RandomNumberGeneratorModel.LAGGED_FIBONACCI
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
