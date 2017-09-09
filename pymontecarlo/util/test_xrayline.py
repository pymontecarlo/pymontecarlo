#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.util.xrayline import XrayLine, find_lowest_energy_known_xrayline

# Globals and constants variables.

class TestXrayLineModule(TestCase):

    def testfind_lowest_energy_known_xrayline(self):
        xrayline = find_lowest_energy_known_xrayline([6])
        self.assertEqual(xrayline, XrayLine(6, 'Ka1'))

        xrayline = find_lowest_energy_known_xrayline([13])
        self.assertEqual(xrayline, XrayLine(13, 'Ll'))

        xrayline = find_lowest_energy_known_xrayline([13], minimum_energy_eV=1e3)
        self.assertEqual(xrayline, XrayLine(13, 'Ka1'))

class TestXrayLine(TestCase):

    def setUp(self):
        super().setUp()

        self.x = XrayLine(13, 'Ka1')

    def testskeleton(self):
        self.assertEqual(13, self.x.element.atomic_number)

        self.assertEqual(2, self.x.line.source_subshell.n)
        self.assertEqual(1, self.x.line.destination_subshell.n)

    def test__hash__(self):
        K = pyxray.AtomicSubshell(1, 0, 1)
        L3 = pyxray.AtomicSubshell(2, 1, 3)
        line = pyxray.XrayTransition(L3, K)
        x = XrayLine(pyxray.Element(13), line)
        self.assertEqual(hash(x), hash(self.x))

    def testiupac(self):
        self.assertEqual('Al K\u2013L3', self.x.iupac)

    def testsiegbahn(self):
        self.assertEqual('Al K\u03b11', self.x.siegbahn)

    def test__eq__(self):
        K = pyxray.AtomicSubshell(1, 0, 1)
        L3 = pyxray.AtomicSubshell(2, 1, 3)
        line = pyxray.XrayTransition(L3, K)
        x = XrayLine(pyxray.Element(13), line)
        self.assertEqual(x, self.x)

    def test__ne__(self):
        K = pyxray.AtomicSubshell(1, 0, 1)
        L3 = pyxray.AtomicSubshell(2, 1, 3)
        line = pyxray.XrayTransition(L3, K)
        x = XrayLine(pyxray.Element(14), line)
        self.assertNotEqual(x, self.x)

        K = pyxray.AtomicSubshell(1, 0, 1)
        L3 = pyxray.AtomicSubshell(3, 1, 3)
        line = pyxray.XrayTransition(L3, K)
        x = XrayLine(pyxray.Element(13), line)
        self.assertNotEqual(x, self.x)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
