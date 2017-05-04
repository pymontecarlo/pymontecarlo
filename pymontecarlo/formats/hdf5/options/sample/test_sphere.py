#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.sample.sphere import SphereSampleHDF5Handler
from pymontecarlo.options.sample.sphere import SphereSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestSphereSampleHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = SphereSampleHDF5Handler()
        sample = SphereSample(Material.pure(29), 50e-9, 0.1, 0.2)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
