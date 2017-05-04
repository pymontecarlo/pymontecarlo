#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.energy_loss import EnergyLossModelSeriesHandler
from pymontecarlo.options.model.energy_loss import EnergyLossModel

# Globals and constants variables.

class TestEnergyLossModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = EnergyLossModelSeriesHandler()
        model = EnergyLossModel.BETHE1930
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
