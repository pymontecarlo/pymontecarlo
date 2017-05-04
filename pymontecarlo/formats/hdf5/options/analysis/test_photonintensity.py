#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.analysis.photonintensity import PhotonIntensityAnalysisHDF5Handler
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis

# Globals and constants variables.

class TestPhotonIntensityAnalysisHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = PhotonIntensityAnalysisHDF5Handler()
        detector = self.create_basic_photondetector()
        analysis = PhotonIntensityAnalysis(detector)
        analysis2 = self.convert_parse_hdf5handler(handler, analysis)
        self.assertEqual(analysis2, analysis)

#        import h5py
#        with h5py.File('/tmp/sample.h5', 'w') as f:
#            handler.convert(sample, f)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
