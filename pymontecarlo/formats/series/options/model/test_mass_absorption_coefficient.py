#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.mass_absorption_coefficient import MassAbsorptionCoefficientModelSeriesHandler
from pymontecarlo.options.model.mass_absorption_coefficient import MassAbsorptionCoefficientModel

# Globals and constants variables.

class TestMassAbsorptionCoefficientModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = MassAbsorptionCoefficientModelSeriesHandler()
        model = MassAbsorptionCoefficientModel.BASTIN_HEIJLIGERS1989
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
