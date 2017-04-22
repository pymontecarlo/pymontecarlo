#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.energy_loss import EnergyLossModelHtmlHandler
from pymontecarlo.options.model.energy_loss import EnergyLossModel

# Globals and constants variables.

class TestEnergyLossModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = EnergyLossModelHtmlHandler()
        model = EnergyLossModel.BETHE1930
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
