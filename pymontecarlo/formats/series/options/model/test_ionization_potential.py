#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.ionization_potential import IonizationPotentialModelSeriesHandler
from pymontecarlo.options.model.ionization_potential import IonizationPotentialModel

# Globals and constants variables.

class TestIonizationPotentialModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = IonizationPotentialModelSeriesHandler()
        model = IonizationPotentialModel.BERGER_SELTZER1964
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
