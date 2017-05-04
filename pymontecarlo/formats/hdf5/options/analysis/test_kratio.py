#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.hdf5.options.analysis.kratio import KRatioAnalysisHDF5Handler
from pymontecarlo.options.analysis.kratio import KRatioAnalysis
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestKRatioAnalysisHDF5Handler(TestCase):

    def testconvert_parse_no_standards(self):
        handler = KRatioAnalysisHDF5Handler()
        detector = self.create_basic_photondetector()
        analysis = KRatioAnalysis(detector)
        analysis2 = self.convert_parse_hdf5handler(handler, analysis)
        self.assertEqual(analysis2, analysis)


    def testconvert_parse(self):
        handler = KRatioAnalysisHDF5Handler()
        detector = self.create_basic_photondetector()
        standard_materials = {29: Material.from_formula('CuZn'),
                              28: Material.from_formula('NiAl')}
        analysis = KRatioAnalysis(detector, standard_materials)
        analysis2 = self.convert_parse_hdf5handler(handler, analysis)
        self.assertEqual(analysis2, analysis)

#        import h5py
#        with h5py.File('/tmp/analysis.h5', 'w') as f:
#            handler.convert(analysis, f)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
