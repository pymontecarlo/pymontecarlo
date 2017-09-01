#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.sample.verticallayers import VerticalLayerSampleSeriesHandler
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample
from pymontecarlo.options.material import Material

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)
GERMANIUM = Material.pure(32)

class TestVerticalLayerSampleSeriesHandler(TestCase):

    def testconvert(self):
        handler = VerticalLayerSampleSeriesHandler()
        sample = VerticalLayerSample(COPPER, ZINC, depth_m=0.3, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(GERMANIUM, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        s = handler.convert(sample)
        self.assertEqual(13, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
