#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.sample.horizontallayers import HorizontalLayerSampleHDF5Handler
from pymontecarlo.options.sample.horizontallayers import HorizontalLayerSample
from pymontecarlo.options.material import Material, VACUUM

# Globals and constants variables.
COPPER = Material.pure(29)
ZINC = Material.pure(30)
GALLIUM = Material.pure(31)

class TestHorizontalLayerSampleHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = HorizontalLayerSampleHDF5Handler()
        sample = HorizontalLayerSample(COPPER, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(ZINC, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

    def testconvert_parse_same_layer(self):
        handler = HorizontalLayerSampleHDF5Handler()
        sample = HorizontalLayerSample(COPPER, tilt_rad=0.1, azimuth_rad=0.2)
        layer = sample.add_layer(ZINC, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        sample.layers.append(layer)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

    def testconvert_parse_same_material(self):
        handler = HorizontalLayerSampleHDF5Handler()
        sample = HorizontalLayerSample(COPPER, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(ZINC, 20e-9)
        sample.add_layer(COPPER, 50e-9)
        sample.add_layer(ZINC, 30e-9)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

    def testconvert_parse_vacuum(self):
        handler = HorizontalLayerSampleHDF5Handler()
        sample = HorizontalLayerSample(COPPER, tilt_rad=0.1, azimuth_rad=0.2)
        sample.add_layer(VACUUM, 20e-9)
        sample.add_layer(GALLIUM, 50e-9)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
