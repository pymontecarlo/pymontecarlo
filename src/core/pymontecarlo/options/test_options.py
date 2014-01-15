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

from pymontecarlo.options.xmlmapper import mapper
from pymontecarlo.options.options import Options # , OptionsSequence
from pymontecarlo.options.detector import BackscatteredElectronEnergyDetector
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.model import ELASTIC_CROSS_SECTION

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
        limit = list(self.ops.limits.iterclass(ShowersLimit))[0]
        self.assertEqual(5678, limit.showers)

        self.assertEqual(1, len(self.ops.models))
        models = list(self.ops.models.iterclass(ELASTIC_CROSS_SECTION))
        self.assertEqual(1, len(models))
        self.assertEqual(ELASTIC_CROSS_SECTION.rutherford, models[0])

    def testcopy(self):
        uuid = self.ops.uuid
        ops = copy.copy(self.ops)

        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)
        self.assertEqual(self.ops.beam, ops.beam)

        self.assertNotEqual(uuid, ops.uuid)
        self.assertEqual(uuid, self.ops.uuid)

        ops.beam.energy_eV = 5678
        self.assertAlmostEqual(5678, self.ops.beam.energy_eV, 4)
        self.assertAlmostEqual(5678, ops.beam.energy_eV, 4)

    def testdeepcopy(self):
        uuid = self.ops.uuid
        ops = copy.deepcopy(self.ops)

        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)
        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)
        self.assertNotEqual(self.ops.beam, ops.beam)

        self.assertNotEqual(uuid, ops.uuid)
        self.assertEqual(uuid, self.ops.uuid)

        ops.beam.energy_eV = 5678
        self.assertAlmostEqual(1234, self.ops.beam.energy_eV, 4)
        self.assertAlmostEqual(5678, ops.beam.energy_eV, 4)

    def testname(self):
        # Test unicode name
        uname = '\u03b1\u03b2\u03b3'
        self.ops.name = uname

        self.assertEqual(uname, self.ops.name)
        self.assertEqual(uname, str(self.ops))

    def testuuid(self):
        uuid = self.ops.uuid
        self.assertEqual(uuid, self.ops.uuid)

    def testdetectors(self):
        dets = list(self.ops.detectors.iterclass(BackscatteredElectronEnergyDetector))
        self.assertEqual(1, len(dets))
        self.assertEqual('bse', dets[0][0])

        dets = list(self.ops.detectors.iterclass(ShowersLimit))
        self.assertEqual(0, len(dets))

    def testdetectors_multiple(self):
        self.ops.detectors['bse'] = \
            [BackscatteredElectronEnergyDetector((0, 1234), 1000),
             BackscatteredElectronEnergyDetector((1234, 5678), 2000)]

        dets = list(self.ops.detectors.iterclass(BackscatteredElectronEnergyDetector))
        self.assertEqual(2, len(dets))
        self.assertEqual('bse', dets[0][0])
        self.assertEqual('bse', dets[1][0])

    def testlimits(self):
        self.ops.limits.add(ShowersLimit(1234))
        self.assertEqual(2, len(self.ops.limits))

        limits = list(self.ops.limits.iterclass(ShowersLimit))
        self.assertEqual(2, len(limits))

    def testmodels(self):
        self.ops.models.add(ELASTIC_CROSS_SECTION.mott_drouin1993)
        self.assertEqual(2, len(self.ops.models))
        models = list(self.ops.models.iterclass(ELASTIC_CROSS_SECTION))
        self.assertEqual(2, len(models))

    def testfrom_xml(self):
        uuid = self.ops.uuid
        element = mapper.to_xml(self.ops)
        ops = mapper.from_xml(element)

        self.assertEqual("Test", ops.name)
        self.assertEqual(uuid, ops.uuid)

        self.assertAlmostEqual(1234, ops.beam.energy_eV, 4)
#
        self.assertEqual(1, len(ops.detectors))
        det = ops.detectors['bse']
        self.assertAlmostEqual(0, det.limits_eV[0], 4)
        self.assertAlmostEqual(1234, det.limits_eV[1], 4)
        self.assertEqual(1000, det.channels)

        self.assertEqual(1, len(ops.limits))
        limits = list(ops.limits.iterclass(ShowersLimit))
        self.assertEqual(1, len(limits))
        self.assertEqual(5678, limits[0].showers)
#
        self.assertEqual(1, len(ops.models))
        models = list(ops.models.iterclass(ELASTIC_CROSS_SECTION))
        self.assertEqual(1, len(models))
        self.assertEqual(ELASTIC_CROSS_SECTION.rutherford, models[0])

    def testto_xml(self):
        element = mapper.to_xml(self.ops)

        self.assertEqual('Test', element.get('name'))
#
        self.assertEqual('xsi:nil', element.get('uuid'))
#
        children = list(element.find('beam'))
        self.assertEqual(1, len(children))
#
        children = list(element.find('geometry'))
        self.assertEqual(1, len(children))

        children = list(element.find('detectors'))
        self.assertEqual(1, len(children))

        children = list(element.find('limits'))
        self.assertEqual(1, len(children))
#
        children = list(element.find('models'))
        self.assertEqual(1, len(children))

# class TestOptionsSequence(TestCase):
#
#    def setUp(self):
#        TestCase.setUp(self)
#
#        self.ops_seq = OptionsSequence()
#
#        self.ops_seq.append(Options('test1'), param1=3.0, param2=4)
#        self.ops_seq.append(Options('test2'), param1=5.0)
#
#    def tearDown(self):
#        TestCase.tearDown(self)
#
#    def test__len__(self):
#        self.assertEqual(2, len(self.ops_seq))
#
#    def test__repr__(self):
#        self.assertEqual('<OptionsSequence(2 options)>', repr(self.ops_seq))
#
#    def test__getitem__(self):
#        self.assertEqual('test1', self.ops_seq[0].name)
#        self.assertEqual('test2', self.ops_seq[1].name)
#        self.assertRaises(IndexError, self.ops_seq.__getitem__, 2)
#
#    def test__delitem__(self):
#        del self.ops_seq[0]
#        self.assertEqual('test2', self.ops_seq[0].name)
#        self.assertAlmostEqual(5.0, self.ops_seq.params[0]['param1'], 4)
#
#    def testappend(self):
#        self.ops_seq.append(Options('test3'), param2=6.0)
#        self.assertEqual('test3', self.ops_seq[2].name)
#        self.assertAlmostEqual(6.0, self.ops_seq.params[2]['param2'], 4)
#
#    def testinsert(self):
#        self.ops_seq.insert(1, Options('test3'), param2=6.0)
#        self.assertEqual('test3', self.ops_seq[1].name)
#        self.assertAlmostEqual(6.0, self.ops_seq.params[1]['param2'], 4)
#
#    def testremove(self):
#        ops = Options('test3')
#        self.ops_seq.append(ops, param2=6.0)
#        self.ops_seq.remove(ops)
#        self.assertEqual(2, len(self.ops_seq))
#
#    def testpop(self):
#        self.ops_seq.pop(0)
#        self.assertEqual('test2', self.ops_seq[0].name)
#        self.assertAlmostEqual(5.0, self.ops_seq.params[0]['param1'], 4)
#
#    def testparameters(self):
#        self.assertAlmostEqual(3.0, self.ops_seq.params[0]['param1'], 4)
#        self.assertEqual(4, self.ops_seq.params[0]['param2'])
#        self.assertAlmostEqual(5.0, self.ops_seq.params[1]['param1'], 4)
#        self.assertRaises(KeyError, self.ops_seq.params[1].__getitem__, 'param2')
#        self.assertAlmostEqual(6.0, self.ops_seq.params[1].get('param2', 6.0), 4)
#
#    def testto_xml(self):
#        element = self.ops_seq.to_xml()
#
#        self.assertEqual(2, len(element.get('identifiers').split(',')))
#        self.assertEqual(2, len(list(element.iter('{http://pymontecarlo.sf.net}options'))))
#
#    def testfrom_xml(self):
#        element = self.ops_seq.to_xml()
#        ops_seq = OptionsSequence.from_xml(element)
#
#        self.assertEqual('test1', ops_seq[0].name)
#        self.assertEqual('test2', ops_seq[1].name)
#        self.assertAlmostEqual(3.0, ops_seq.params[0]['param1'], 4)
#        self.assertEqual(4, ops_seq.params[0]['param2'])
#        self.assertAlmostEqual(5.0, ops_seq.params[1]['param1'], 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
