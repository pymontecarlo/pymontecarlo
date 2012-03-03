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
import copy

# Third party modules.

# Local modules.
from pymontecarlo.util.subshell import get_subshell

# Globals and constants variables.
from pymontecarlo.util.subshell import _IUPACS, _ORBITALS, _SIEGBAHNS

class TestSubshell(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(get_subshell(1) is get_subshell(1))

    def testcopy(self):
        subshell = get_subshell(1)
        copied = copy.copy(subshell)
        self.assertTrue(subshell is copied)

        copied = copy.deepcopy(subshell)
        self.assertTrue(subshell is copied)

    def testindex(self):
        for i in range(1, 31):
            self.assertEqual(i, get_subshell(i).index)

    def testorbital(self):
        for i in range(1, 31):
            self.assertEqual(_ORBITALS[i - 1], get_subshell(i).orbital)

    def testiupac(self):
        for i in range(1, 31):
            self.assertEqual(_IUPACS[i - 1], get_subshell(i).iupac)

    def testsiegbahn(self):
        for i in range(1, 31):
            self.assertEqual(_SIEGBAHNS[i - 1], get_subshell(i).siegbahn)

    def testfamily(self):
        # K
        self.assertEqual('K', get_subshell(1).family)

        # L
        for i in range(2, 5):
            self.assertEqual("L", get_subshell(i).family)

        # M
        for i in range(5, 10):
            self.assertEqual("M", get_subshell(i).family)

        # N
        for i in range(10, 17):
            self.assertEqual("N", get_subshell(i).family)

        # O
        for i in range(17, 24):
            self.assertEqual("O", get_subshell(i).family)

        # P
        for i in range(24, 29):
            self.assertEqual("P", get_subshell(i).family)

        # Q
        self.assertEqual('Q', get_subshell(29).family)

        # outer
        self.assertEqual(None, get_subshell(30).family)

    def testget_subshell(self):
        for i, orbital in enumerate(_ORBITALS):
            s = get_subshell(orbital=orbital)
            self.assertEqual(i + 1, s.index)

        for i, iupac in enumerate(_IUPACS):
            s = get_subshell(iupac=iupac)
            self.assertEqual(i + 1, s.index)

        for i, siegbahn in enumerate(_SIEGBAHNS):
            s = get_subshell(siegbahn=siegbahn)
            self.assertEqual(i + 1, s.index)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
