#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.bremsstrahlung_emission import BremsstrahlungEmissionModelHtmlHandler
from pymontecarlo.options.model.bremsstrahlung_emission import BremsstrahlungEmissionModel

# Globals and constants variables.

class TestBremsstrahlungEmissionModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = BremsstrahlungEmissionModelHtmlHandler()
        model = BremsstrahlungEmissionModel.SELTZER_BERGER1985
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
