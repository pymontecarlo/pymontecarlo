#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.limit.uncertainty import UncertaintyLimit

# Globals and constants variables.

class TestUncertaintyLimit(TestCase):

    def setUp(self):
        super().setUp()

        self.l = UncertaintyLimit(13, 'Ka1', None, 0.02)

    def testskeleton(self):
        self.assertEqual(13, self.l.atomic_number)
        self.assertEqual('Ka1', self.l.transition)
        self.assertIsNone(self.l.detector)
        self.assertAlmostEqual(0.02, self.l.uncertainty, 4)

    def test__repr__(self):
        expected = '<UncertaintyLimit(Al K–L3 <= 2.0%)>'
        self.assertEqual(expected, repr(self.l))

    def test__eq__(self):
        l = UncertaintyLimit(13, 'Ka1', None, 0.02)
        self.assertEqual(l, self.l)

    def test__ne__(self):
        l = UncertaintyLimit(14, 'Ka1', None, 0.02)
        self.assertNotEqual(l, self.l)

        l = UncertaintyLimit(13, 'La1', None, 0.02)
        self.assertNotEqual(l, self.l)

        l = UncertaintyLimit(13, 'Ka1', 'detector', 0.02)
        self.assertNotEqual(l, self.l)

        l = UncertaintyLimit(13, 'Ka1', None, 0.03)
        self.assertNotEqual(l, self.l)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
