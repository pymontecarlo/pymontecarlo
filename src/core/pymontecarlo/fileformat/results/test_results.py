#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import tempfile

# Third party modules.
import h5py

# Local modules.
from pymontecarlo.fileformat.results.results import \
    ResultsReader, ResultsWriter, append

from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import \
    PhotonIntensityDetector, TimeDetector, ElectronFractionDetector

from pymontecarlo.results.results import Results
from pymontecarlo.results.result import \
    PhotonIntensityResult, TimeResult, ElectronFractionResult

# Globals and constants variables.

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        ops1 = Options(name='test1')
        ops1.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))
        ops1.detectors['det2'] = TimeDetector()
        ops1.detectors['det3'] = ElectronFractionDetector()

        results1 = {}
        results1['det1'] = PhotonIntensityResult()
        results1['det2'] = TimeResult()
        results1['det3'] = ElectronFractionResult()

        ops2 = Options(name='test2')
        ops2.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))

        results2 = {}
        results2['det1'] = PhotonIntensityResult()

        self.obj = Results(Options(name='base'),
                           [(ops1, results1), (ops2, results2)])

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testappend(self):
        with tempfile.NamedTemporaryFile() as f:
            self.obj.write(f.name)

            # Append
            ops3 = Options(name='test3')
            newobj = Results(self.obj.options, [(ops3, {})])
            append(newobj, f.name)

            obj = Results.read(f.name)

            self.assertEqual(3, len(obj))

class TestResultsReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestResultsReader, cls).setUpClass()

        ops1 = Options(name='test1')
        ops1.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))
        ops1.detectors['det2'] = TimeDetector()
        ops1.detectors['det3'] = ElectronFractionDetector()

        results1 = {}
        results1['det1'] = PhotonIntensityResult()
        results1['det2'] = TimeResult()
        results1['det3'] = ElectronFractionResult()

        ops2 = Options(name='test2')
        ops2.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))

        results2 = {}
        results2['det1'] = PhotonIntensityResult()

        cls.results = Results(Options(name='base'),
                              [(ops1, results1), (ops2, results2)])

        cls.group = h5py.File('test.h5', 'a', driver='core', backing_store=False)

        writer = ResultsWriter()
        writer.convert(cls.results, cls.group)
        writer.join()

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.reader = ResultsReader()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.reader.can_parse(self.group))

    def testparse(self):
        ops_uuid = self.results.options.uuid
        ops1_uuid = self.results[0].options.uuid

        self.reader.parse(self.group)
        obj = self.reader.get()

        self.assertEqual(2, len(obj))
        self.assertEqual('test1', obj[0].options.name)
        self.assertEqual('test2', obj[1].options.name)

        self.assertIn('det1', obj[0])
        self.assertIn('det2', obj[0])
        self.assertIn('det3', obj[0])
        self.assertIn('det1', obj[1])

        self.assertEqual(ops_uuid, obj.options.uuid)
        self.assertEqual(ops1_uuid, obj[0].options.uuid)

class TestResultsWriter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        ops1 = Options(name='test1')
        ops1.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))
        ops1.detectors['det2'] = TimeDetector()
        ops1.detectors['det3'] = ElectronFractionDetector()

        results1 = {}
        results1['det1'] = PhotonIntensityResult()
        results1['det2'] = TimeResult()
        results1['det3'] = ElectronFractionResult()

        ops2 = Options(name='test2')
        ops2.detectors['det1'] = PhotonIntensityDetector((0, 1), (0, 1))

        results2 = {}
        results2['det1'] = PhotonIntensityResult()

        self.results = Results(Options(name='base'),
                               [(ops1, results1), (ops2, results2)])

        self.writer = ResultsWriter()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_convert(self):
        self.assertTrue(self.writer.can_convert(self.results))

    def testconvert(self):
        group = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.writer.convert(self.results, group)
        self.writer.join()

        self.assertEqual(2, len(group))
        self.assertEqual(2, len(group.attrs['identifiers']))

        subgroup = group['result-' + group.attrs['identifiers'][0]]
        self.assertEqual(3, len(subgroup))
        self.assertIn('det1', subgroup)
        self.assertIn('det2', subgroup)
        self.assertIn('det3', subgroup)

        subgroup = group['result-' + group.attrs['identifiers'][1]]
        self.assertEqual(1, len(subgroup))
        self.assertIn('det1', subgroup)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
