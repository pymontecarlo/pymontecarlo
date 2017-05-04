#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.direction_cosine import DirectionCosineModelSeriesHandler
from pymontecarlo.options.model.direction_cosine import DirectionCosineModel

# Globals and constants variables.

class TestDirectionCosineModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = DirectionCosineModelSeriesHandler()
        model = DirectionCosineModel.DEMERS2000
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
