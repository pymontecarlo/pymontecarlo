#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.quant.runner.iterator import Heinrich1972Iterator, Pouchou1991Iterator

# Globals and constants variables.

class TestHeinrich1972Iterator(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        experimental_kratios = {29: 0.2, 79: 0.8}
        initial_composition = {29: 0.5, 79: 0.5}

        self.it = Heinrich1972Iterator(experimental_kratios, initial_composition)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testnext(self):
        calculated_kratios = {29: 0.3, 79: 0.7}
        composition = self.it.next(calculated_kratios)

        self.assertAlmostEqual(0.3684, composition[29], 4)
        self.assertAlmostEqual(0.6316, composition[79], 4)

class TestPouchou1991Iterator(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        experimental_kratios = {29: 0.2, 79: 0.8}
        initial_composition = {29: 0.5, 79: 0.5}

        self.it = Pouchou1991Iterator(experimental_kratios, initial_composition)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testnext(self):
        calculated_kratios = {29: 0.3, 79: 0.7}
        composition = self.it.next(calculated_kratios)

        self.assertAlmostEqual(0.3684, composition[29], 4)
        self.assertAlmostEqual(0.3864, composition[79], 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
