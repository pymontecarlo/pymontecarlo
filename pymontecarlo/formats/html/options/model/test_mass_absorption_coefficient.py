#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.mass_absorption_coefficient import MassAbsorptionCoefficientModelHtmlHandler
from pymontecarlo.options.model.mass_absorption_coefficient import MassAbsorptionCoefficientModel

# Globals and constants variables.

class TestMassAbsorptionCoefficientModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = MassAbsorptionCoefficientModelHtmlHandler()
        model = MassAbsorptionCoefficientModel.BASTIN_HEIJLIGERS1989
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
