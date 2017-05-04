#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.limit.showers import ShowersLimit, ShowersLimitBuilder

# Globals and constants variables.

class TestShowersLimit(TestCase):

    def setUp(self):
        super().setUp()

        self.l = ShowersLimit(1000)

    def testskeleton(self):
        self.assertEqual(1000, self.l.number_trajectories)

    def test__repr__(self):
        expected = '<ShowersLimit(1000 trajectories)>'
        self.assertEqual(expected, repr(self.l))

    def test__eq__(self):
        l = ShowersLimit(1000)
        self.assertEqual(l, self.l)

    def test__ne__(self):
        l = ShowersLimit(1001)
        self.assertNotEqual(l, self.l)

class TestShowersLimitBuilder(TestCase):

    def testbuild(self):
        b = ShowersLimitBuilder()
        b.add_number_trajectories(1000)
        self.assertEqual(1, len(b))
        self.assertEqual(1, len(b.build()))

    def testbuild2(self):
        b = ShowersLimitBuilder()
        b.add_number_trajectories(1000)
        b.add_number_trajectories(1000)
        b.add_number_trajectories(2000)
        self.assertEqual(2, len(b))
        self.assertEqual(2, len(b.build()))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
