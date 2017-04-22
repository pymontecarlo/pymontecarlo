#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.ionization_cross_section import IonizationCrossSectionModelHtmlHandler
from pymontecarlo.options.model.ionization_cross_section import IonizationCrossSectionModel

# Globals and constants variables.

class TestIonizationCrossSectionModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = IonizationCrossSectionModelHtmlHandler()
        model = IonizationCrossSectionModel.BOTE_SALVAT2008
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
