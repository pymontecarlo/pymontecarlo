#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.inelastic_cross_section import InelasticCrossSectionModelSeriesHandler
from pymontecarlo.options.model.inelastic_cross_section import InelasticCrossSectionModel

# Globals and constants variables.

class TestInelasticCrossSectionModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = InelasticCrossSectionModelSeriesHandler()
        model = InelasticCrossSectionModel.STERNHEIMER_LILJEQUIST1952
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
