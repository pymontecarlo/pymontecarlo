#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.limit.showers import ShowersLimit

# Globals and constants variables.

class TestShowersLimit(TestCase):

    def setUp(self):
        super().setUp()

        self.l = ShowersLimit(1000)

    def testskeleton(self):
        self.assertEqual(1000, self.l.showers)

    def test__repr__(self):
        expected = '<ShowersLimit(1000 trajectories)>'
        self.assertEqual(expected, repr(self.l))

    def test__eq__(self):
        l = ShowersLimit(1000)
        self.assertEqual(l, self.l)

    def test__ne__(self):
        l = ShowersLimit(1001)
        self.assertNotEqual(l, self.l)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
