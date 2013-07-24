#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.input.bound import bound
from pymontecarlo.input.xmlmapper import mapper

# Globals and constants variables.

class Testbound(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.a = bound(-5, 5)
        self.b = bound(6, -6)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(-5, self.a.low)
        self.assertEqual(-5, self.a.lower)
        self.assertEqual(5, self.a.high)
        self.assertEqual(5, self.a.upper)

        self.assertEqual(-6, self.b.low)
        self.assertEqual(-6, self.b.lower)
        self.assertEqual(6, self.b.high)
        self.assertEqual(6, self.b.upper)

        self.assertRaises(AttributeError, setattr, self.b, 'lower', 0)

    def testfrom_xml(self):
        element = mapper.to_xml(self.a)
        a = mapper.from_xml(element)

        self.assertEqual(-5, a.low)
        self.assertEqual(-5, a.lower)
        self.assertEqual(5, a.high)
        self.assertEqual(5, a.upper)

    def testto_xml(self):
        element = mapper.to_xml(self.a)

        self.assertEqual(-5, int(element.get('lower')))
        self.assertEqual(5, int(element.get('upper')))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
