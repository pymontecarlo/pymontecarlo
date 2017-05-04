#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.sample.inclusion import InclusionSampleSeriesHandler
from pymontecarlo.options.sample.inclusion import InclusionSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestInclusionSampleSeriesHandler(TestCase):

    def testconvert(self):
        handler = InclusionSampleSeriesHandler()
        sample = InclusionSample(Material.pure(29), Material.pure(30), 50e-9, 0.1, 0.2)
        s = handler.convert(sample)
        self.assertEqual(7, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
