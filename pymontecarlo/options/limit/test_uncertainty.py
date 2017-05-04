#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.limit.uncertainty import UncertaintyLimit
from pymontecarlo.util.xrayline import XrayLine

# Globals and constants variables.

class TestUncertaintyLimit(TestCase):

    def setUp(self):
        super().setUp()

        self.d = self.create_basic_photondetector()
        self.l = UncertaintyLimit(XrayLine(13, 'Ka1'), self.d, 0.02)

    def testskeleton(self):
        self.assertEqual(XrayLine(13, 'Ka1'), self.l.xrayline)
        self.assertEqual(self.d, self.l.detector)
        self.assertAlmostEqual(0.02, self.l.uncertainty, 4)

    def test__repr__(self):
        expected = '<UncertaintyLimit(Al K–L3 <= 2.0%)>'
        self.assertEqual(expected, repr(self.l))

    def test__eq__(self):
        l = UncertaintyLimit(XrayLine(13, 'Ka1'), self.d, 0.02)
        self.assertEqual(l, self.l)

    def test__ne__(self):
        l = UncertaintyLimit(XrayLine(14, 'Ka1'), self.d, 0.02)
        self.assertNotEqual(l, self.l)

        l = UncertaintyLimit(XrayLine(13, 'La1'), self.d, 0.02)
        self.assertNotEqual(l, self.l)

        l = UncertaintyLimit(XrayLine(13, 'Ka1'), 'detector', 0.02)
        self.assertNotEqual(l, self.l)

        l = UncertaintyLimit(XrayLine(13, 'Ka1'), self.d, 0.03)
        self.assertNotEqual(l, self.l)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
