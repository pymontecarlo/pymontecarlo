#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.
from pyxray.transition import Transition

# Local modules.
from pymontecarlo.util.photon_range import photon_range

from pymontecarlo.options.material import Material

# Globals and constants variables.

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testphoton_range(self):
        material = Material.pure(29)
        transition = Transition(29, siegbahn='Ka1')
        self.assertAlmostEqual(8.4064e-7, photon_range(20e3, material, transition), 10)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
