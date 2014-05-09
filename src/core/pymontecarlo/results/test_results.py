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

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import \
    PhotonIntensityDetector, TimeDetector, ElectronFractionDetector

from pymontecarlo.results.results import Results, ResultsContainer
from pymontecarlo.results.result import \
    PhotonIntensityResult, TimeResult, ElectronFractionResult

# Globals and constants variables.

class TestResultsContainer(TestCase):

    def setUp(self):
        TestCase.setUp(self)

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

        self.results = ResultsContainer(self.ops, results)

    def tearDown(self):
        TestCase.tearDown(self)

    def testoptions(self):
        # frozen
        self.assertRaises(ValueError, setattr,
                          self.results.options.beam, 'energy_eV', 6.0)

class TestResults(TestCase):

    def setUp(self):
        TestCase.setUp(self)

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

    def test__len__(self):
        self.assertEqual(2, len(self.results))

    def test__repr__(self):
        self.assertEqual('<Results(2 results)>', repr(self.results))

    def test__getitem__(self):
        self.assertEqual('test1', self.results[0].options.name)
        self.assertEqual('test2', self.results[1].options.name)
        self.assertRaises(IndexError, self.results.__getitem__, 2)

    def testreadwrite(self):
        with tempfile.NamedTemporaryFile() as f:
            self.results.write(f.name)
            obj = Results.read(f.name)

        self.assertEqual(2, len(obj))
        self.assertEqual('test1', obj[0].options.name)
        self.assertEqual('test2', obj[1].options.name)

        self.assertIn('det1', obj[0])
        self.assertIn('det2', obj[0])
        self.assertIn('det3', obj[0])
        self.assertIn('det1', obj[1])

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
