#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.ionization_cross_section import IonizationCrossSectionModelSeriesHandler
from pymontecarlo.options.model.ionization_cross_section import IonizationCrossSectionModel

# Globals and constants variables.

class TestIonizationCrossSectionModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = IonizationCrossSectionModelSeriesHandler()
        model = IonizationCrossSectionModel.BOTE_SALVAT2008
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
