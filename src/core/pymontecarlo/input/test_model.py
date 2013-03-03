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

from pymontecarlo.input.model import \
    Model, ModelCategory, ModelType, NO_MODEL_TYPE, get_all_models

# Globals and constants variables.

class TestModelType(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.mtype = ModelType('type1')

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('type1', self.mtype.name)

    def test__str__(self):
        self.assertEqual('type1', str(self.mtype))

    def test__repr__(self):
        self.assertEqual('<ModelType(type1)>', repr(self.mtype))

    def test__eq__(self):
        self.assertTrue(ModelType('type1') == self.mtype)
        self.assertFalse(ModelType('type2') == self.mtype)

    def test__ne__(self):
        self.assertFalse(ModelType('type1') != self.mtype)
        self.assertTrue(ModelType('type2') != self.mtype)

    def testregister(self):
        m = Model('name1', 'ref1')
        self.mtype.register(m)

        self.assertEqual(1, len(self.mtype))
        self.assertTrue(m in self.mtype)
        self.assertEqual([m], list(self.mtype))

        self.assertRaises(ValueError, self.mtype.register, m)

    def testNO_MODEL_TYPE(self):
        self.assertEqual('no type', NO_MODEL_TYPE.name)
        self.assertFalse(NO_MODEL_TYPE)

class TestModel(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.m1 = Model('name1', 'ref1')
        self.m2 = Model('name2')

        self.mtype = ModelType('type1')
        self.mtype.register(self.m2)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('name1', self.m1.name)
        self.assertEqual('ref1', self.m1.reference)
        self.assertRaises(ValueError, self.m1.__getattribute__, 'type')

        self.assertEqual('name2', self.m2.name)
        self.assertEqual('', self.m2.reference)
        self.assertEqual(self.mtype, self.m2.type)

    def test__str__(self):
        self.assertEqual('name1', str(self.m1))
        self.assertEqual('name2', str(self.m2))

    def test__repr__(self):
        self.assertEqual('<Model(name1)>', repr(self.m1))
        self.assertEqual('<Model(name2)>', repr(self.m2))

    def test__eq__(self):
        self.assertTrue(self.m1 == Model('name1', 'ref1'))
        self.assertFalse(self.m2 == Model('name2'))

    def test__ne__(self):
        self.assertFalse(self.m1 != Model('name1', 'ref1'))
        self.assertTrue(self.m2 != Model('name2'))

    def testfrom_xml(self):
        element = self.m2.to_xml()
        m2 = Model.from_xml(element)

        self.assertEqual('name2', m2.name)
        self.assertEqual('', m2.reference)
        self.assertEqual(self.mtype, m2.type)

    def testto_xml(self):
        self.assertRaises(IOError, self.m1.to_xml)

        element = self.m2.to_xml()
        self.assertEqual('name2', element.get('name'))
        self.assertEqual(str(self.mtype), element.get('type'))

class TestModelCategory(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.mtype = ModelType('type1')
        self.mcat = ModelCategory(self.mtype)

        self.m1 = Model('name1', 'ref1')
        self.m2 = Model('name2')

        self.mcat.m1 = self.m1
        self.mcat.m2 = self.m2

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEquals(self.mtype, self.mcat.type)

        self.assertEqual(2, len(self.mcat))
        self.assertTrue(self.m1 in self.mcat)
        self.assertTrue(self.m2 in self.mcat)

        self.assertEqual(2, len(self.mtype))
        self.assertTrue(self.m1 in self.mtype)
        self.assertTrue(self.m2 in self.mtype)

        models = get_all_models()
        self.assertTrue(self.m1 in models)
        self.assertTrue(self.m2 in models)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
