#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.sample.verticallayers import VerticalLayerSampleHDF5Handler
from pymontecarlo.options.sample.verticallayers import VerticalLayerSample
from pymontecarlo.options.material import Material

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)
GERMANIUM = Material.pure(32)

class TestVerticalLayerSampleHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = VerticalLayerSampleHDF5Handler()
        sample = VerticalLayerSample(COPPER, ZINC, depth_m=0.3, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(GERMANIUM, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

    def testconvert_parse_infinite_depth(self):
        handler = VerticalLayerSampleHDF5Handler()
        sample = VerticalLayerSample(COPPER, ZINC, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(GERMANIUM, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

    def testconvert_parse_same_layer(self):
        handler = VerticalLayerSampleHDF5Handler()
        sample = VerticalLayerSample(COPPER, ZINC, depth_m=0.3, tilt_rad=0.1, azimuth_rad=0.2)
        layer = sample.add_layer(GERMANIUM, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        sample.layers.append(layer)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

    def testconvert_parse_same_material(self):
        handler = VerticalLayerSampleHDF5Handler()
        sample = VerticalLayerSample(COPPER, ZINC, depth_m=0.3, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(GERMANIUM, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        sample.add_layer(GERMANIUM, 30e-9)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
