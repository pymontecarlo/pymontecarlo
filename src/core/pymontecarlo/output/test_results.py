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
import tempfile
import shutil
import os

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import \
    PhotonIntensityDetector, TimeDetector, ElectronFractionDetector

from pymontecarlo.output.results import Results
from pymontecarlo.output.result import \
    PhotonIntensityResult, TimeResult, ElectronFractionResult

# Globals and constants variables.

class TestResults(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        # Temporary directory
        self.tmpdir = tempfile.mkdtemp()

        # Options
        ops = Options()
        ops.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))
        ops.detectors['det2'] = TimeDetector()
        ops.detectors['det3'] = ElectronFractionDetector()

        # Results
        results = {}
        results['det1'] = PhotonIntensityResult()
        results['det2'] = TimeResult()
        results['det3'] = ElectronFractionResult()

        self.results = Results(ops, results)

        self.results_h5 = os.path.join(os.path.dirname(__file__),
                                       '../testdata/results.h5')

    def tearDown(self):
        TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    def testsave(self):
        h5filepath = os.path.join(self.tmpdir, 'results.h5')
        self.results.save(h5filepath)

        hdf5file = h5py.File(h5filepath, 'r')

        self.assertIn('det1', hdf5file)
        self.assertIn('det2', hdf5file)
        self.assertIn('det3', hdf5file)

        hdf5file.close()

    def testload(self):
        results = Results.load(self.results_h5)
        self.assertEqual(6, len(results))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
