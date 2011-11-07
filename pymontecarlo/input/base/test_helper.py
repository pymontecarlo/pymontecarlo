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

# Third party modules.

# Local modules.
from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.material import Material

# Globals and constants variables.

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options(name="Test")
        self.ops.beam.energy = 20e3

        mat = Material('Brass', {29: 0.5, 30: 0.4, 50: 0.1},
                       absorption_energy_electron=1000)
        self.ops.geometry.material = mat

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
