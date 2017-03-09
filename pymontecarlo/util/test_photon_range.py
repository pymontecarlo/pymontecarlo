#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.util.photon_range import photon_range
from pymontecarlo.util.xrayline import XrayLine
from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestModule(TestCase):

    def testphoton_range(self):
        material = Material.pure(29)
        xrayline = XrayLine(29, 'Ka1')
        self.assertAlmostEqual(8.4064e-7, photon_range(20e3, material, xrayline), 10)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
