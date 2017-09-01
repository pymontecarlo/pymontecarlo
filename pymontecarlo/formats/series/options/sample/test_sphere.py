#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.sample.sphere import SphereSampleSeriesHandler
from pymontecarlo.options.sample.sphere import SphereSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestSphereSampleSeriesHandler(TestCase):

    def testconvert(self):
        handler = SphereSampleSeriesHandler()
        sample = SphereSample(Material.pure(29), 50e-9, 0.1, 0.2)
        s = handler.convert(sample)
        self.assertEqual(5, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
