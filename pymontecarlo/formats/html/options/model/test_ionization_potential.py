#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.ionization_potential import IonizationPotentialModelHtmlHandler
from pymontecarlo.options.model.ionization_potential import IonizationPotentialModel

# Globals and constants variables.

class TestIonizationPotentialModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = IonizationPotentialModelHtmlHandler()
        model = IonizationPotentialModel.BERGER_SELTZER1964
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
