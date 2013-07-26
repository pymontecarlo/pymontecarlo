#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
from operator import attrgetter

# Third party modules.

# Local modules.
from pymontecarlo.input.expander import Expander
from pymontecarlo.input.options import Options

# Globals and constants variables.

class Test(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options("op1")
        self.ops.beam.energy_eV = [5e3, 10e3, 15e3]

        self.expander = Expander()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testexpand(self):
        opss = self.expander.expand(self.ops)
        self.assertEqual(3, len(opss))

        names = map(attrgetter('name'), opss)
        self.assertIn('op1+energy_eV=5000.0', names)
        self.assertIn('op1+energy_eV=10000.0', names)
        self.assertIn('op1+energy_eV=15000.0', names)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
