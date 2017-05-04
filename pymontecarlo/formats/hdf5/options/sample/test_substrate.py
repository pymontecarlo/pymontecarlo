#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.sample.substrate import SubstrateSampleHDF5Handler
from pymontecarlo.options.sample.substrate import SubstrateSample
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestSubstrateSampleHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = SubstrateSampleHDF5Handler()
        sample = SubstrateSample(Material.pure(29), 0.1, 0.2)
        sample2 = self.convert_parse_hdf5handler(handler, sample)
        self.assertEqual(sample2, sample)

#        import h5py
#        with h5py.File('/tmp/sample.h5', 'w') as f:
#            handler.convert(sample, f)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
