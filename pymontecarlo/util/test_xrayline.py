#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.util.xrayline import \
    XrayLine, set_preferred_encoding, set_preferred_notation

# Globals and constants variables.

class TestXrayLine(TestCase):

    def setUp(self):
        super().setUp()

        self.x = XrayLine(13, 'Ka1')

    def testskeleton(self):
        self.assertEqual(13, self.x.element.atomic_number)

        self.assertEqual(2, self.x.transition.source_subshell.n)
        self.assertEqual(1, self.x.transition.destination_subshell.n)

    def test__hash__(self):
        K = pyxray.AtomicSubshell(1, 0, 1)
        L3 = pyxray.AtomicSubshell(2, 1, 3)
        transition = pyxray.Transition(L3, K)
        x = XrayLine(pyxray.Element(13), transition)
        self.assertEqual(hash(x), hash(self.x))

    def test__str__(self):
        set_preferred_notation('siegbahn')
        set_preferred_encoding('ascii')
        self.assertEqual('Al Ka1', str(self.x))

        set_preferred_notation('siegbahn')
        set_preferred_encoding('latex')
        self.assertEqual('Al \\ensuremath{\\mathrm{K}\\alpha_1}', str(self.x))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
