#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.random_number_generator import RandomNumberGeneratorModelHtmlHandler
from pymontecarlo.options.model.random_number_generator import RandomNumberGeneratorModel

# Globals and constants variables.

class TestRandomNumberGeneratorModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = RandomNumberGeneratorModelHtmlHandler()
        model = RandomNumberGeneratorModel.LAGGED_FIBONACCI
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
