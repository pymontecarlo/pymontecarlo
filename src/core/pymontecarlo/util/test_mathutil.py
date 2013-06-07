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
from pymontecarlo.util.mathutil import vector3d, vector2d

# Globals and constants variables.

class Testvector3d(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.u = vector3d(1, 2, 3)
        self.v = vector3d(-1, 2, -3)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(1, self.u.x)
        self.assertEqual(2, self.u.y)
        self.assertEqual(3, self.u.z)
    
    def test__add__(self):
        w = self.u + self.v
        self.assertEqual(0, w.x)
        self.assertEqual(4, w.y)
        self.assertEqual(0, w.z)

        w = self.u + 5
        self.assertEqual(6, w.x)
        self.assertEqual(7, w.y)
        self.assertEqual(8, w.z)

    def test__sub__(self):
        w = self.u - self.v
        self.assertEqual(2, w.x)
        self.assertEqual(0, w.y)
        self.assertEqual(6, w.z)

        w = self.u - 5
        self.assertEqual(-4, w.x)
        self.assertEqual(-3, w.y)
        self.assertEqual(-2, w.z)

    def test__rsub__(self):
        w = self.v - self.u
        self.assertEqual(-2, w.x)
        self.assertEqual(0, w.y)
        self.assertEqual(-6, w.z)

        w = 5 - self.u
        self.assertEqual(4, w.x)
        self.assertEqual(3, w.y)
        self.assertEqual(2, w.z)

    def test__mul__(self):
        w = self.u * self.v
        self.assertEqual(-1, w.x)
        self.assertEqual(4, w.y)
        self.assertEqual(-9, w.z)

        w = self.u * 5
        self.assertEqual(5, w.x)
        self.assertEqual(10, w.y)
        self.assertEqual(15, w.z)

    def test__div__(self):
        w = self.u / vector3d(2.0, 2.0, 2.0)
        self.assertAlmostEqual(0.5, w.x, 4)
        self.assertAlmostEqual(1.0, w.y, 4)
        self.assertAlmostEqual(1.5, w.z, 4)

        w = self.u / 2.0
        self.assertAlmostEqual(0.5, w.x, 4)
        self.assertAlmostEqual(1.0, w.y, 4)
        self.assertAlmostEqual(1.5, w.z, 4)

    def test__neg__(self):
        w = -self.u
        self.assertEqual(-1, w.x)
        self.assertEqual(-2, w.y)
        self.assertEqual(-3, w.z)

    def test__abs__(self):
        self.assertAlmostEqual(3.74166, abs(self.u), 4)
        self.assertAlmostEqual(3.74166, self.u.magnitude(), 4)

    def testnormalize(self):
        w = self.u.normalize()
        self.assertAlmostEqual(0.26726, w.x, 4)
        self.assertAlmostEqual(0.53452, w.y, 4)
        self.assertAlmostEqual(0.80178, w.z, 4)

    def testdot(self):
        self.assertEqual(-6, self.u.dot(self.v))

class Testvector2d(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.u = vector2d(1, 2)
        self.v = vector2d(-1, 2)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(1, self.u.x)
        self.assertEqual(2, self.u.y)

    def test__add__(self):
        w = self.u + self.v
        self.assertEqual(0, w.x)
        self.assertEqual(4, w.y)

        w = self.u + 5
        self.assertEqual(6, w.x)
        self.assertEqual(7, w.y)

    def test__sub__(self):
        w = self.u - self.v
        self.assertEqual(2, w.x)
        self.assertEqual(0, w.y)

        w = self.u - 5
        self.assertEqual(-4, w.x)
        self.assertEqual(-3, w.y)

    def test__rsub__(self):
        w = self.v - self.u
        self.assertEqual(-2, w.x)
        self.assertEqual(0, w.y)

        w = 5 - self.u
        self.assertEqual(4, w.x)
        self.assertEqual(3, w.y)

    def test__mul__(self):
        w = self.u * self.v
        self.assertEqual(-1, w.x)
        self.assertEqual(4, w.y)

        w = self.u * 5
        self.assertEqual(5, w.x)
        self.assertEqual(10, w.y)

    def test__div__(self):
        w = self.u / vector2d(2.0, 2.0)
        self.assertAlmostEqual(0.5, w.x, 4)
        self.assertAlmostEqual(1.0, w.y, 4)

        w = self.u / 2.0
        self.assertAlmostEqual(0.5, w.x, 4)
        self.assertAlmostEqual(1.0, w.y, 4)

    def test__neg__(self):
        w = -self.u
        self.assertEqual(-1, w.x)
        self.assertEqual(-2, w.y)

    def test__abs__(self):
        self.assertAlmostEqual(2.23607, abs(self.u), 4)
        self.assertAlmostEqual(2.23607, self.u.magnitude(), 4)

    def testnormalize(self):
        w = self.u.normalize()
        self.assertAlmostEqual(0.44721, w.x, 4)
        self.assertAlmostEqual(0.89443, w.y, 4)

    def testdot(self):
        self.assertEqual(3, self.u.dot(self.v))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
