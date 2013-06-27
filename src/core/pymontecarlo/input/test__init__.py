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
from pymontecarlo.input import mapper
from pymontecarlo.util.mathutil import vector3d, vector2d

# Globals and constants variables.

class Testvector2d(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.u = vector2d(1, 2)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)
        
    def testto_xml(self):
        element = mapper.to_xml(self.u)

        self.assertEqual('1', element.get('x'))
        self.assertEqual('2', element.get('y'))

    def testfrom_xml(self):
        element = mapper.to_xml(self.u)
        u = mapper.from_xml(element)

        self.assertEqual(1, u.x)
        self.assertEqual(2, u.y)

class Testvector3d(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.u = vector3d(1, 2, 3)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testto_xml(self):
        element = mapper.to_xml(self.u)

        self.assertEqual('1', element.get('x'))
        self.assertEqual('2', element.get('y'))
        self.assertEqual('3', element.get('z'))

    def testfrom_xml(self):
        element = mapper.to_xml(self.u)
        u = mapper.from_xml(element)

        self.assertEqual(1, u.x)
        self.assertEqual(2, u.y)
        self.assertEqual(3, u.z)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
