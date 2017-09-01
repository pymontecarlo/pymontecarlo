#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.bremsstrahlung_emission import BremsstrahlungEmissionModelSeriesHandler
from pymontecarlo.options.model.bremsstrahlung_emission import BremsstrahlungEmissionModel

# Globals and constants variables.

class TestBremsstrahlungEmissionModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = BremsstrahlungEmissionModelSeriesHandler()
        model = BremsstrahlungEmissionModel.SELTZER_BERGER1985
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
