#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

# Globals and constants variables.

class TestOptions(TestCase):

    def setUp(self):
        super().setUp()

        self.options = self._create_basic_options()

    def testskeleton(self):
        self.assertAlmostEqual(15e3, self.options.beam.energy_eV, 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
