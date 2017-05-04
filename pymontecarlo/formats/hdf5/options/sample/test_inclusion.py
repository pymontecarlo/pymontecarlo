#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.sample.inclusion import InclusionSampleHDF5Handler
from pymontecarlo.options.sample.inclusion import InclusionSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestInclusionSampleHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = InclusionSampleHDF5Handler()
        sample = InclusionSample(Material.pure(29), Material.pure(30), 50e-9, 0.1, 0.2)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
