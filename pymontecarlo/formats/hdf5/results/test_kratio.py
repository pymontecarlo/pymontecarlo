#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.

from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.results.kratio import KRatioResultHDF5Handler
from pymontecarlo.options.analysis.kratio import KRatioAnalysis
from pymontecarlo.results.kratio import KRatioResultBuilder

# Globals and constants variables.

class TestKRatioResultHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = KRatioResultHDF5Handler()
        analysis = KRatioAnalysis(self.create_basic_photondetector())
        b = KRatioResultBuilder(analysis)
        b.add_kratio((29, 'Ka1'), 2.0, 5.0)
        b.add_kratio((29, 'Ka'), 4.0, 5.0)
        result = b.build()
        result2 = self.convert_parse_hdf5handler(handler, result)

        self.assertEqual(len(result), len(result2))
        self.assertSetEqual(set(result.keys()), set(result2.keys()))

        self.assertAlmostEqual(result[(29, 'Ka1')], result2[(29, 'Ka1')], 4)
        self.assertAlmostEqual(result[(29, 'Ka')], result2[(29, 'Ka')], 4)

#        import h5py
#        with h5py.File('/tmp/result.h5', 'w') as f:
#            handler.convert(result, f)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
