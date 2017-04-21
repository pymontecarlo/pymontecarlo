#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.sample.substrate import SubstrateSampleSeriesHandler
from pymontecarlo.options.sample.substrate import SubstrateSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestSubstrateSampleSeriesHandler(TestCase):

    def testconvert(self):
        handler = SubstrateSampleSeriesHandler()
        sample = SubstrateSample(Material.pure(29), 0.1, 0.2)
        s = handler.convert(sample)
        self.assertEqual(4, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
