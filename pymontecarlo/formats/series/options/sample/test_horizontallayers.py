#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.sample.horizontallayers import HorizontalLayerSampleSeriesHandler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)

class TestHorizontalLayerSampleSeriesHandler(TestCase):

    def testconvert(self):
        handler = HorizontalLayerSampleSeriesHandler()
        sample = HorizontalLayerSample(COPPER, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(ZINC, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        s = handler.convert(sample)
        self.assertEqual(10, len(s))

    def testconvert_vacuum(self):
        handler = HorizontalLayerSampleSeriesHandler()
        sample = HorizontalLayerSample(COPPER, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(VACUUM, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        s = handler.convert(sample)
        self.assertEqual(8, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
