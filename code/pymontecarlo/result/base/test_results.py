#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
from math import radians
import tempfile
from zipfile import ZipFile
import os

# Third party modules.

# Local modules.
from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.detector import \
    PhotonIntensityDetector, TimeDetector, ElectronFractionDetector
from pymontecarlo.result.base.results import Results
from pymontecarlo.result.base.result import \
    PhotonIntensityResult, TimeResult, ElectronFractionResult

import DrixUtilities.Files as Files

# Globals and constants variables.

class TestResults(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        # Temporary files
        _fp, self.tmpzip = tempfile.mkstemp('.zip')

        # Detectors
        det1 = PhotonIntensityDetector((radians(35), radians(45)),
                                       (0, radians(360.0)))
        self.det2 = TimeDetector()
        det3 = ElectronFractionDetector()

        # Options
        self.ops = Options()
        self.ops.beam.energy = 1234
        self.ops.detectors['det1'] = det1
        self.ops.detectors['det2'] = self.det2
        self.ops.detectors['det3'] = det3

        # Results
        results = {}
        results['det1'] = PhotonIntensityResult(det1)
        results['det2'] = TimeResult(self.det2)
        results['det3'] = ElectronFractionResult(det3)

        self.results = Results(self.ops, results)

        self.results_zip = \
            Files.getCurrentModulePath(__file__, '../../testdata/results.zip')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

        os.remove(self.tmpzip)

    def testskeleton(self):
        self.assertTrue(True)

    def test__init__invalidkey(self):
        results = {}
        results['det4'] = PhotonIntensityResult(self.det2)

        self.assertRaises(ValueError, Results, self.ops, results)

    def testsave(self):
        with open(self.tmpzip, 'w') as fp:
            self.results.save(fp)

        with open(self.tmpzip, 'r') as fp:
            zipfile = ZipFile(fp, 'r')

            namelist = zipfile.namelist()
            self.assertTrue('keys.ini' in namelist)
            self.assertTrue('det1.csv' in namelist)
            self.assertTrue('det2.xml' in namelist)
            self.assertTrue('det3.xml' in namelist)

            zipfile.close()

    def testload(self):
        with open(self.results_zip, 'r') as fp:
            results = Results.load(fp, self.ops)

        self.assertEqual(3, len(results))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
