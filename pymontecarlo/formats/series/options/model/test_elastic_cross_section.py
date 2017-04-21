#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.elastic_cross_section import ElasticCrossSectionModelSeriesHandler
from pymontecarlo.options.model.elastic_cross_section import ElasticCrossSectionModel

# Globals and constants variables.

class TestElasticCrossSectionModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = ElasticCrossSectionModelSeriesHandler()
        model = ElasticCrossSectionModel.ELSEPA2005
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
