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
from StringIO import StringIO

# Third party modules.

# Local modules.
from pymontecarlo.util.histogram import _Histogram, CountHistogram, SumHistogram

# Globals and constants variables.

class Test_Histogram(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        bins = range(1, 9, 2)
        self.h = _Histogram(bins)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test__repr__(self):
        expected = "Histogram(min=1, max=7, bins=4)"
        self.assertEqual(expected, repr(self.h))

    def test__iadd__(self):
        h1 = _Histogram(range(1, 9, 2))
        h1._values[0] = 1

        self.h += h1
        self.assertEqual(1, self.h._values[0])

        # Test exception
        h1 = _Histogram(range(1, 7, 2))
        self.assertRaises(ValueError, self.h.__iadd__, h1)

    def test_bins(self):
        self.assertEqual(0, self.h._bin(0.0))
        self.assertEqual(1, self.h._bin(1.0))
        self.assertEqual(1, self.h._bin(2.0))
        self.assertEqual(2, self.h._bin(3.0))
        self.assertEqual(2, self.h._bin(4.0))
        self.assertEqual(3, self.h._bin(5.0))
        self.assertEqual(3, self.h._bin(6.0))
        self.assertEqual(4, self.h._bin(7.0))
        self.assertEqual(4, self.h._bin(8.0))

    def test_pprint(self):
        out = StringIO()
        self.h._pprint(self.h._values, out)

        expected = '   < 1\t0.0\n[1, 3[\t0.0\n[3, 5[\t0.0\n[5, 7[\t0.0\n  >= 7\t0.0\n'
        self.assertEqual(expected, out.getvalue())

    def testbins(self):
        self.assertEqual(len(self.h._values), len(self.h.bins))

class TestCountHistogram(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        bins = range(1, 9, 2)
        self.h = CountHistogram(bins)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testadd(self):
        self.h.add(0.0)
        self.assertEqual([1, 0, 0, 0, 0], list(self.h.counts))

        self.h.add(1.0)
        self.assertEqual([1, 1, 0, 0, 0], list(self.h.counts))

        self.h.add(2.0)
        self.assertEqual([1, 2, 0, 0, 0], list(self.h.counts))

        self.h.add(3.0)
        self.assertEqual([1, 2, 1, 0, 0], list(self.h.counts))

        self.h.add(4.0)
        self.assertEqual([1, 2, 2, 0, 0], list(self.h.counts))

        self.h.add(5.0)
        self.assertEqual([1, 2, 2, 1, 0], list(self.h.counts))

        self.h.add(6.0)
        self.assertEqual([1, 2, 2, 2, 0], list(self.h.counts))

        self.h.add(7.0)
        self.assertEqual([1, 2, 2, 2, 1], list(self.h.counts))

        self.h.add(8.0)
        self.assertEqual([1, 2, 2, 2, 2], list(self.h.counts))

class TestSumHistogram(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        bins = range(1, 9, 2)
        self.h = SumHistogram(bins)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testadd(self):
        self.h.add(0.0, 0.5)
        self.assertEqual([0.5, 0, 0, 0, 0], list(self.h._values))
        self.assertEqual([0.25, 0, 0, 0, 0], list(self.h._squares))

        self.h.add(1.0, 0.5)
        self.assertEqual([0.5, 0.5, 0, 0, 0], list(self.h._values))
        self.assertEqual([0.25, 0.25, 0, 0, 0], list(self.h._squares))

        self.h.add(2.0, 0.5)
        self.assertEqual([0.5, 1, 0, 0, 0], list(self.h._values))
        self.assertEqual([0.25, 0.5, 0, 0, 0], list(self.h._squares))

        self.h.add(3.0, 0.5)
        self.assertEqual([0.5, 1, 0.5, 0, 0], list(self.h._values))
        self.assertEqual([0.25, 0.5, 0.25, 0, 0], list(self.h._squares))

        self.h.add(4.0, 0.5)
        self.assertEqual([0.5, 1, 1, 0, 0], list(self.h._values))
        self.assertEqual([0.25, 0.5, 0.5, 0, 0], list(self.h._squares))

        self.h.add(5.0, 0.5)
        self.assertEqual([0.5, 1, 1, 0.5, 0], list(self.h._values))
        self.assertEqual([0.25, 0.5, 0.5, 0.25, 0], list(self.h._squares))

        self.h.add(6.0, 0.5)
        self.assertEqual([0.5, 1, 1, 1, 0], list(self.h._values))
        self.assertEqual([0.25, 0.5, 0.5, 0.5, 0], list(self.h._squares))

        self.h.add(7.0, 0.5)
        self.assertEqual([0.5, 1, 1, 1, 0.5], list(self.h._values))
        self.assertEqual([0.25, 0.5, 0.5, 0.5, 0.25], list(self.h._squares))

        self.h.add(8.0, 0.5)
        self.assertEqual([0.5, 1, 1, 1, 1], list(self.h._values))
        self.assertEqual([0.25, 0.5, 0.5, 0.5, 0.5], list(self.h._squares))

    def testsums(self):
        self.assertEqual([0, 0, 0, 0, 0], list(self.h.sums))

        self.h.add(0.0, 0.5)
        self.h.add(0.0, 0.5)
        self.h.add(1.0, 0.5)
        self.assertEqual([1.0, 0.5, 0, 0, 0], list(self.h.sums))

    def testsquares(self):
        self.assertEqual([0, 0, 0, 0, 0], list(self.h.squares))

        self.h.add(0.0, 0.5)
        self.h.add(0.0, 1.5)
        self.h.add(1.0, 0.5)
        self.assertEqual([0.25 + 2.25, 0.25, 0, 0, 0], list(self.h.squares))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
