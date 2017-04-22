#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.direction_cosine import DirectionCosineModelHtmlHandler
from pymontecarlo.options.model.direction_cosine import DirectionCosineModel

# Globals and constants variables.

class TestDirectionCosineModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = DirectionCosineModelHtmlHandler()
        model = DirectionCosineModel.DEMERS2000
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
