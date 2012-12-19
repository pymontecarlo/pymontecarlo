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
from pymontecarlo.util.xmlutil import objectxml, XMLIO

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
XMLIO.register('ObjectXMLMock', ObjectXMLMock)

class Testobjectxml(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.mock1 = ObjectXMLMock('abc')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testsave(self):
        self.mock1.save('/tmp/mock.xml')

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
