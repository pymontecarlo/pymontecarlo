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
import xml.etree.ElementTree as etree
from io import BytesIO

# Third party modules.

# Local modules.
from pymontecarlo.fileformat.options.model import ModelXMLHandler

from pymontecarlo.options.model import ModelType

# Globals and constants variables.

MTYPE = ModelType('type1')
MTYPE.m1 = ('name1', 'ref1')
MTYPE.m2 = ('name2',)

class TestModelXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = ModelXMLHandler()

        self.obj1 = MTYPE.m1
        self.obj2 = MTYPE.m2

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:model xmlns:mc="http://pymontecarlo.sf.net" name="name1" type="type1" />')
        self.element1 = etree.parse(source).getroot()

        source = BytesIO(b'<mc:model xmlns:mc="http://pymontecarlo.sf.net" name="name2" type="type1" />')
        self.element2 = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element1))
        self.assertTrue(self.h.can_parse(self.element2))

    def testparse(self):
        # Model 1
        obj = self.h.parse(self.element1)

        self.assertEqual('name1', obj.name)
        self.assertEqual('ref1', obj.reference)
        self.assertEqual(MTYPE, obj.type)

        # Model 2
        obj = self.h.parse(self.element2)

        self.assertEqual('name2', obj.name)
        self.assertEqual('', obj.reference)
        self.assertEqual(MTYPE, obj.type)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj1))
        self.assertTrue(self.h.can_convert(self.obj2))

    def testconvert(self):
        # Model 1
        element = self.h.convert(self.obj1)

        self.assertEqual('name1', element.get('name'))
        self.assertEqual(str(MTYPE), element.get('type'))

        # Model 2
        element = self.h.convert(self.obj2)

        self.assertEqual('name2', element.get('name'))
        self.assertEqual(str(MTYPE), element.get('type'))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
