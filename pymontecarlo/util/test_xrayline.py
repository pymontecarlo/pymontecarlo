#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
import pyxray

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.util.xrayline import find_lowest_energy_known_xrayline

# Globals and constants variables.

class TestXrayLineModule(TestCase):

    def testfind_lowest_energy_known_xrayline(self):
        xrayline = find_lowest_energy_known_xrayline([6])
        self.assertEqual(xrayline, pyxray.XrayLine(6, 'Ka1'))

        xrayline = find_lowest_energy_known_xrayline([13])
        self.assertEqual(xrayline, pyxray.XrayLine(13, 'Ll'))

        xrayline = find_lowest_energy_known_xrayline([13], minimum_energy_eV=1e3)
        self.assertEqual(xrayline, pyxray.XrayLine(13, 'Ka1'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
