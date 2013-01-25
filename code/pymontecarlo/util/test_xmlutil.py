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

# Third party modules.

# Local modules.
from pymontecarlo.util.xmlutil import objectxml, XMLIO, Element

# Globals and constants variables.

class ObjectXMLMock(objectxml):

    def __init__(self, val):
        self.val = val

    @classmethod
    def __loadxml__(cls, element, *args, **kwargs):
        val = element.get('val')
        return cls(val)

    def __savexml__(self, element, *args, **kwargs):
        element.set('val', str(self.val))

XMLIO.reset()
XMLIO.register('{http://test.org}ObjectXMLMock', ObjectXMLMock)
XMLIO.register_namespace('test', 'http://test.org')

class Testobjectxml(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.mock1 = ObjectXMLMock('abc')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testto_xml(self):
        element = self.mock1.to_xml()
        self.assertEqual('{http://test.org}ObjectXMLMock', element.tag)
        self.assertEqual('abc', element.get('val'))

    def testfrom_xml(self):
        element = Element('{http://test.org}ObjectXMLMock', val='abc')
        mock1 = XMLIO.from_xml(element)
        self.assertEqual('abc', mock1.val)

        element = Element('ObjectXMLMock', val='abc')
        self.assertRaises(ValueError, XMLIO.from_xml, element)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
