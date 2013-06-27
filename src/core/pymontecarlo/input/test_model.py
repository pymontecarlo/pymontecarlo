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

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.input.model import ModelType
from pymontecarlo.input import mapper

# Globals and constants variables.

MTYPE = ModelType('type1')
MTYPE.m1 = ('name1', 'ref1')
MTYPE.m2 = ('name2',)

class TestModelType(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test__str__(self):
        self.assertEqual('type1', str(MTYPE))

    def test__repr__(self):
        self.assertEqual('<ModelType(type1)>', repr(MTYPE))

    def test__eq__(self):
        self.assertTrue(ModelType('type1') == MTYPE)
        self.assertFalse(ModelType('type2') == MTYPE)

    def test__ne__(self):
        self.assertFalse(ModelType('type1') != MTYPE)
        self.assertTrue(ModelType('type2') != MTYPE)

    def test__setattr__(self):
        self.assertRaises(ValueError, setattr, MTYPE, 'm1', ('name3',))
        self.assertRaises(ValueError, setattr, MTYPE, 'm3', ('name1',))
        
    def test__len__(self):
        self.assertEqual(2, len(MTYPE))
        
    def test__contains__(self):
        self.assertTrue(MTYPE.m1 in MTYPE)
        self.assertTrue(MTYPE.m2 in MTYPE)
        self.assertTrue('name1' in MTYPE)
        self.assertTrue('name2' in MTYPE)
        self.assertFalse('name3' in MTYPE)

class TestModel(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('name1', MTYPE.m1.name)
        self.assertEqual('ref1', MTYPE.m1.reference)
        self.assertIs(MTYPE, MTYPE.m1.type)

        self.assertEqual('name2', MTYPE.m2.name)
        self.assertEqual('', MTYPE.m2.reference)
        self.assertIs(MTYPE, MTYPE.m2.type)

    def test__str__(self):
        self.assertEqual('name1', str(MTYPE.m1))
        self.assertEqual('name2', str(MTYPE.m2))

    def test__repr__(self):
        self.assertEqual('<Model(name1)>', repr(MTYPE.m1))
        self.assertEqual('<Model(name2)>', repr(MTYPE.m2))

    def testfrom_xml(self):
        element = mapper.to_xml(MTYPE.m1)
        m1 = mapper.from_xml(element)

        self.assertEqual('name1', m1.name)
        self.assertEqual('ref1', m1.reference)
        self.assertEqual(MTYPE, m1.type)

        element = mapper.to_xml(MTYPE.m2)
        m2 = mapper.from_xml(element)

        self.assertEqual('name2', m2.name)
        self.assertEqual('', m2.reference)
        self.assertEqual(MTYPE, m2.type)
#
    def testto_xml(self):
        element = mapper.to_xml(MTYPE.m1)
        self.assertEqual('name1', element.get('name'))
        self.assertEqual(str(MTYPE), element.get('type'))

        element = mapper.to_xml(MTYPE.m2)
        self.assertEqual('name2', element.get('name'))
        self.assertEqual(str(MTYPE), element.get('type'))
#
if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
