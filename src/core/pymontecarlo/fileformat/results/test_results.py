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
    ResultsHDF5Handler, load, save

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

    def testloadsave(self):
        with tempfile.NamedTemporaryFile() as f:
            save(self.obj, f.name)
            obj = load(f.name)

        self.assertEqual(2, len(obj))
        self.assertEqual('test1', obj[0].options.name)
        self.assertEqual('test2', obj[1].options.name)

        self.assertIn('det1', obj[0])
        self.assertIn('det2', obj[0])
        self.assertIn('det3', obj[0])
        self.assertIn('det1', obj[1])

class TestResultsHDF5Handler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.hdf5file = h5py.File('test.h5', 'a', driver='core', backing_store=False)
        self.h = ResultsHDF5Handler()

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

        self.group = self.h.convert(self.obj, self.hdf5file)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.hdf5file.close()

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.group))

    def testparse(self):
        ops_uuid = self.obj.options.uuid
        ops1_uuid = self.obj[0].options.uuid
        obj = self.h.parse(self.group)

        self.assertEqual(2, len(obj))
        self.assertEqual('test1', obj[0].options.name)
        self.assertEqual('test2', obj[1].options.name)

        self.assertIn('det1', obj[0])
        self.assertIn('det2', obj[0])
        self.assertIn('det3', obj[0])
        self.assertIn('det1', obj[1])

        self.assertEqual(ops_uuid, obj.options.uuid)
        self.assertEqual(ops1_uuid, obj[0].options.uuid)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        group = self.hdf5file

        self.assertEqual(2, len(group))
        self.assertEqual(2, len(group.attrs['identifiers']))

        subgroup = group[group.attrs['identifiers'][0]]
        self.assertEqual(3, len(subgroup))
        self.assertIn('det1', subgroup)
        self.assertIn('det2', subgroup)
        self.assertIn('det3', subgroup)

        subgroup = group[group.attrs['identifiers'][1]]
        self.assertEqual(1, len(subgroup))
        self.assertIn('det1', subgroup)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
