#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.model.fluorescence import FluorescenceModelSeriesHandler
from pymontecarlo.options.model.fluorescence import FluorescenceModel

# Globals and constants variables.

class TestFluorescenceModelSeriesHandler(TestCase):

    def testconvert(self):
        handler = FluorescenceModelSeriesHandler()
        model = FluorescenceModel.FLUORESCENCE_COMPTON
        s = handler.convert(model)
        self.assertEqual(1, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
