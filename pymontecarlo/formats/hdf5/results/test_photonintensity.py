#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.results.photonintensity import \
    EmittedPhotonIntensityResultHDF5Handler, GeneratedPhotonIntensityResultHDF5Handler
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.results.photonintensity import GeneratedPhotonIntensityResultBuilder

# Globals and constants variables.

class TestEmittedPhotonIntensityResultHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = EmittedPhotonIntensityResultHDF5Handler()
        result = self.create_basic_photonintensityresult()
        result2 = self.convert_parse_hdf5handler(handler, result)

        self.assertEqual(len(result), len(result2))
        self.assertSetEqual(set(result.keys()), set(result2.keys()))

#        import h5py
#        with h5py.File('/tmp/result.h5', 'w') as f:
#            handler.convert(result, f)

class TestGeneratedPhotonIntensityResultHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = GeneratedPhotonIntensityResultHDF5Handler()
        analysis = PhotonIntensityAnalysis(self.create_basic_photondetector())
        b = GeneratedPhotonIntensityResultBuilder(analysis)
        b.add_intensity((29, 'Ka1'), 10.0, 0.1)
        b.add_intensity((29, 'Ka2'), 20.0, 0.2)
        b.add_intensity((29, 'Kb1'), 40.0, 0.5)
        result = b.build()
        result2 = self.convert_parse_hdf5handler(handler, result)

        self.assertEqual(len(result), len(result2))
        self.assertSetEqual(set(result.keys()), set(result2.keys()))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
