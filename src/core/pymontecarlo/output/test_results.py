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

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.input.options import Options
from pymontecarlo.input.detector import \
    PhotonIntensityDetector, TimeDetector, ElectronFractionDetector

from pymontecarlo.output.results import Results, _ResultsContainer
from pymontecarlo.output.result import \
    PhotonIntensityResult, TimeResult, ElectronFractionResult

# Globals and constants variables.

class Test_ResultsContainer(TestCase):

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

        self.results = _ResultsContainer(self.ops, results)

    def tearDown(self):
        TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testoptions(self):
        # frozen
        self.assertRaises(AttributeError, setattr,
                          self.results.options.beam, 'energy_eV', 6.0)

class TestResults(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

        # Results 1
        self.ops1 = Options(name='test1')
        self.ops1.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))
        self.ops1.detectors['det2'] = TimeDetector()
        self.ops1.detectors['det3'] = ElectronFractionDetector()

        results1 = {}
        results1['det1'] = PhotonIntensityResult()
        results1['det2'] = TimeResult()
        results1['det3'] = ElectronFractionResult()

        # Results 2
        ops2 = Options(name='test2')
        ops2.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))

        results2 = {}
        results2['det1'] = PhotonIntensityResult()

        # Base options
        self.ops = Options(name='base')

        # Sequence
        list_results = [(self.ops1, results1), (ops2, results2)]
        self.results = Results(self.ops, list_results)

    def tearDown(self):
        TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test__len__(self):
        self.assertEqual(2, len(self.results))

    def test__repr__(self):
        self.assertEqual('<Results(2 results)>', repr(self.results))

    def test__getitem__(self):
        self.assertEqual('test1', self.results[0].options.name)
        self.assertEqual('test2', self.results[1].options.name)
        self.assertRaises(IndexError, self.results.__getitem__, 2)

    def testsave_load(self):
        # Save
        ops_uuid = self.ops.uuid
        ops1_uuid = self.ops1.uuid
        filepath = os.path.join(self.tmpdir, 'results.h5')
        self.results.save(filepath)

        # Load
        results = Results.load(filepath)

        # Test
        self.assertEqual('test1', results[0].options.name)
        self.assertEqual('test2', results[1].options.name)
        self.assertRaises(IndexError, results.__getitem__, 2)

        self.assertIn('det1', results[0])
        self.assertIn('det2', results[0])
        self.assertIn('det3', results[0])
        self.assertIn('det1', results[1])

        self.assertEqual(ops_uuid, results.options.uuid)
        self.assertEqual(ops1_uuid, results[0].options.uuid)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
