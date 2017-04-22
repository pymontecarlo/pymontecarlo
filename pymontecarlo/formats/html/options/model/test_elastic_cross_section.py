#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.html.options.model.elastic_cross_section import ElasticCrossSectionModelHtmlHandler
from pymontecarlo.options.model.elastic_cross_section import ElasticCrossSectionModel

# Globals and constants variables.

class TestElasticCrossSectionModelHtmlHandler(TestCase):

    def testconvert(self):
        handler = ElasticCrossSectionModelHtmlHandler()
        model = ElasticCrossSectionModel.ELSEPA2005
        root = handler.convert(model)
        self.assertEqual(1, len(root.children))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
