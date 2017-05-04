#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.fluorescence import FluorescenceModelHtmlHandler
from pymontecarlo.options.model.fluorescence import FluorescenceModel

# Globals and constants variables.

class TestFluorescenceModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = FluorescenceModelHtmlHandler()
        model = FluorescenceModel.FLUORESCENCE_COMPTON
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
