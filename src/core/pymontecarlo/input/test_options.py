#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import copy

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.input.options import Options, OptionsSequence
from pymontecarlo.input.detector import BackscatteredElectronEnergyDetector
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.model import ELASTIC_CROSS_SECTION, ELASTIC_CROSS_SECTION_TYPE

# Globals and constants variables.

class TestOptions(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.ops = Options(name="Test")
        self.ops.beam.energy_eV = 1234

        self.ops.detectors['bse'] = BackscatteredElectronEnergyDetector((0, 1234), 1000)
        self.ops.limits.add(ShowersLimit(5678))
        self.ops.models.add(ELASTIC_CROSS_SECTION.rutherford)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)

        self.assertEqual(1, len(self.ops.detectors))
        det = self.ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(self.ops.limits))
        limit = self.ops.limits.find(ShowersLimit)
        self.assertEqual(5678, limit.showers)

        self.assertEqual(1, len(self.ops.models))
        model = self.ops.models.find(ELASTIC_CROSS_SECTION_TYPE)
        self.assertEqual(ELASTIC_CROSS_SECTION.rutherford, model)

    def testfrom_xml(self):
        element = self.ops.to_xml()
        ops = Options.from_xml(element)

        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)

        self.assertEqual(1, len(ops.detectors))
        det = ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(ops.limits))
        limit = ops.limits.find(ShowersLimit)
        self.assertEqual(5678, limit.showers)

        self.assertEqual(1, len(ops.models))
        model = ops.models.find(ELASTIC_CROSS_SECTION_TYPE)
        self.assertEqual(ELASTIC_CROSS_SECTION.rutherford, model)

    def testcopy(self):
        ops = copy.deepcopy(self.ops)
        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)
        self.assertNotEqual(self.ops.beam, ops.beam)

        ops.beam.energy_eV = 5678
        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)
        self.assertAlmostEqual(5678, ops.beam.energy_eV, 4)

    def testname(self):
        # Test unicode name
        uname = '\u03b1\u03b2\u03b3'
        self.ops.name = uname

        self.assertEqual(uname, self.ops.name)
        self.assertEqual(uname, unicode(self.ops))
        self.assertEqual(uname, str(self.ops))

    def testdetectors(self):
        dets = self.ops.detectors.findall(BackscatteredElectronEnergyDetector)
        self.assertEqual(1, len(dets))

        key = self.ops.detectors.find(dets.values()[0])
        self.assertEqual('bse', key)

        dets = self.ops.detectors.findall(ShowersLimit)
        self.assertEqual(0, len(dets))

        self.assertRaises(KeyError, self.ops.detectors.__setitem__, 'options', None)

    def testlimits(self):
        self.ops.limits.add(ShowersLimit(1234))
        self.assertEqual(1, len(self.ops.limits))
        limit = self.ops.limits.find(ShowersLimit)
        self.assertEqual(1234, limit.showers)

    def testmodels(self):
        self.ops.models.add(ELASTIC_CROSS_SECTION.mott_drouin1993)
        self.assertEqual(1, len(self.ops.models))
        model = self.ops.models.find(ELASTIC_CROSS_SECTION_TYPE)
        self.assertEqual(ELASTIC_CROSS_SECTION.mott_drouin1993, model)

    def testto_xml(self):
        element = self.ops.to_xml()

        self.assertEqual('Test', element.get('name'))

        children = list(element.find('beam'))
        self.assertEqual(1, len(children))

        children = list(element.find('geometry'))
        self.assertEqual(1, len(children))

        children = list(element.find('detectors'))
        self.assertEqual(1, len(children))
        self.assertEqual('bse', children[0].get('_key'))

        children = list(element.find('limits'))
        self.assertEqual(1, len(children))

        children = list(element.find('models'))
        self.assertEqual(1, len(children))

class TestOptionsSequence(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.ops_seq = OptionsSequence()

        self.ops_seq.append(Options('test1'), param1=3.0, param2=4)
        self.ops_seq.append(Options('test2'), param1=5.0)

    def tearDown(self):
        TestCase.tearDown(self)

    def test__len__(self):
        self.assertEqual(2, len(self.ops_seq))

    def test__repr__(self):
        self.assertEqual('<OptionsSequence(2 options)>', repr(self.ops_seq))

    def test__getitem__(self):
        self.assertEqual('test1', self.ops_seq[0].name)
        self.assertEqual('test2', self.ops_seq[1].name)
        self.assertRaises(IndexError, self.ops_seq.__getitem__, 2)

    def test__delitem__(self):
        del self.ops_seq[0]
        self.assertEqual('test2', self.ops_seq[0].name)
        self.assertAlmostEqual(5.0, self.ops_seq.params[0]['param1'], 4)

    def testappend(self):
        self.ops_seq.append(Options('test3'), param2=6.0)
        self.assertEqual('test3', self.ops_seq[2].name)
        self.assertAlmostEqual(6.0, self.ops_seq.params[2]['param2'], 4)

    def testinsert(self):
        self.ops_seq.insert(1, Options('test3'), param2=6.0)
        self.assertEqual('test3', self.ops_seq[1].name)
        self.assertAlmostEqual(6.0, self.ops_seq.params[1]['param2'], 4)

    def testremove(self):
        ops = Options('test3')
        self.ops_seq.append(ops, param2=6.0)
        self.ops_seq.remove(ops)
        self.assertEqual(2, len(self.ops_seq))

    def testpop(self):
        self.ops_seq.pop(0)
        self.assertEqual('test2', self.ops_seq[0].name)
        self.assertAlmostEqual(5.0, self.ops_seq.params[0]['param1'], 4)

    def testget_parameter(self):
        self.assertAlmostEqual(3.0, self.ops_seq.params[0]['param1'], 4)
        self.assertEqual(4, self.ops_seq.params[0]['param2'])
        self.assertAlmostEqual(5.0, self.ops_seq.params[1]['param1'], 4)
        self.assertRaises(KeyError, self.ops_seq.params[1].__getitem__, 'param2')
        self.assertAlmostEqual(6.0, self.ops_seq.params[1].get('param2', 6.0), 4)

    def testto_xml(self):
        element = self.ops_seq.to_xml()

        self.assertEqual(2, len(element.get('identifiers').split(',')))
        self.assertEqual(2, len(list(element.iter('{http://pymontecarlo.sf.net}options'))))

    def testfrom_xml(self):
        element = self.ops_seq.to_xml()
        ops_seq = OptionsSequence.from_xml(element)

        self.assertEqual('test1', ops_seq[0].name)
        self.assertEqual('test2', ops_seq[1].name)
        self.assertAlmostEqual(3.0, ops_seq.params[0]['param1'], 4)
        self.assertEqual(4, ops_seq.params[0]['param2'])
        self.assertAlmostEqual(5.0, ops_seq.params[1]['param1'], 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
