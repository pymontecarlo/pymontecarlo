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

from pymontecarlo.output.results import Results, ResultsSequence
from pymontecarlo.output.result import \
    PhotonIntensityResult, TimeResult, ElectronFractionResult

# Globals and constants variables.

class TestResults(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        # Temporary directory
        self.tmpdir = tempfile.mkdtemp()

        # Options
        self.ops = Options()
        self.ops.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))
        self.ops.detectors['det2'] = TimeDetector()
        self.ops.detectors['det3'] = ElectronFractionDetector()

        # Results
        results = {}
        results['det1'] = PhotonIntensityResult()
        results['det2'] = TimeResult()
        results['det3'] = ElectronFractionResult()

        self.results = Results(self.ops, results)

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

    def testoptions_uuid(self):
        self.assertEqual(self.ops.uuid, self.results.options_uuid)

    def testoptions(self):
        self.assertIsNot(self.ops, self.results.options)

class TestResultsSequence(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

        # Results 1
        ops = Options(name='test1')
        ops.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))
        ops.detectors['det2'] = TimeDetector()
        ops.detectors['det3'] = ElectronFractionDetector()

        results = {}
        results['det1'] = PhotonIntensityResult()
        results['det2'] = TimeResult()
        results['det3'] = ElectronFractionResult()

        results1 = Results(ops, results)

        # Results 2
        ops = Options(name='test2')
        ops.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))

        results = {}
        results['det1'] = PhotonIntensityResult()

        results2 = Results(ops, results)

        # Sequence
        list_results = [results1, results2]
        list_params = [{'param1': 3.0, 'param2': 4}, {'param1': 5.0}]
        self.results_seq = ResultsSequence(list_results, list_params)

    def tearDown(self):
        TestCase.tearDown(self)
#        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test__len__(self):
        self.assertEqual(2, len(self.results_seq))

    def test__repr__(self):
        self.assertEqual('<ResultsSequence(2 results)>', repr(self.results_seq))

    def test__getitem__(self):
        self.assertEqual('test1', self.results_seq[0].options.name)
        self.assertEqual('test2', self.results_seq[1].options.name)
        self.assertRaises(IndexError, self.results_seq.__getitem__, 2)

    def testparameters(self):
        self.assertAlmostEqual(3.0, self.results_seq.params[0]['param1'], 4)
        self.assertEqual(4, self.results_seq.params[0]['param2'])
        self.assertAlmostEqual(5.0, self.results_seq.params[1]['param1'], 4)
        self.assertRaises(KeyError, self.results_seq.params[1].__getitem__, 'param2')
        self.assertAlmostEqual(6.0, self.results_seq.params[1].get('param2', 6.0), 4)

        self.results_seq.params[0]['param1'] = 99.9 # Not store
        self.assertAlmostEqual(3.0, self.results_seq.params[0]['param1'], 4)

    def testsave_load(self):
        # Save
        filepath = os.path.join(self.tmpdir, 'results.h5')
        self.results_seq.save(filepath)

        # Load
        results_seq = ResultsSequence.load(filepath)

        # Test
        self.assertEqual('test1', results_seq[0].options.name)
        self.assertEqual('test2', results_seq[1].options.name)
        self.assertRaises(IndexError, results_seq.__getitem__, 2)

        self.assertAlmostEqual(3.0, results_seq.params[0]['param1'], 4)
        self.assertEqual(4, results_seq.params[0]['param2'])
        self.assertAlmostEqual(5.0, results_seq.params[1]['param1'], 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
