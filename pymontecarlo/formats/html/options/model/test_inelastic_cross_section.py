#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.inelastic_cross_section import InelasticCrossSectionModelHtmlHandler
from pymontecarlo.options.model.inelastic_cross_section import InelasticCrossSectionModel

# Globals and constants variables.

class TestInelasticCrossSectionModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = InelasticCrossSectionModelHtmlHandler()
        model = InelasticCrossSectionModel.STERNHEIMER_LILJEQUIST1952
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
