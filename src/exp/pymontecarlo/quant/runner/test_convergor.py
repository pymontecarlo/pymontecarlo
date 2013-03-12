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
from pymontecarlo.quant.runner.convergor import \
    CompositionConvergor, KRatioConvergor

# Globals and constants variables.

class TestCompositionConvergor(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        experimental_kratios = {29: (0.2, 0.0), 79: (0.8, 0.0)}
        initial_composition = {29: 0.5, 79: 0.5}

        self.cnv = CompositionConvergor(experimental_kratios, initial_composition, 0.01)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testhas_converged(self):
        kratios = {29: (0.15, 0.0), 79: (0.85, 0.0)}
        composition = {29: 0.49, 79: 0.51}
        self.cnv.add_iteration(kratios, composition)
        self.assertFalse(self.cnv.has_converged())

        kratios = {29: (0.15, 0.0), 79: (0.85, 0.0)}
        composition = {29: 0.4999, 79: 0.5101}
        self.cnv.add_iteration(kratios, composition)
        self.assertTrue(self.cnv.has_converged())

class TestKRatioConvergor(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        experimental_kratios = {29: (0.2, 0.0), 79: (0.8, 0.0)}
        initial_composition = {29: 0.5, 79: 0.5}

        self.cnv = KRatioConvergor(experimental_kratios, initial_composition, 0.01)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testhas_converged(self):
        kratios = {29: (0.15, 0.0), 79: (0.85, 0.0)}
        composition = {29: 0.49, 79: 0.51}
        self.cnv.add_iteration(kratios, composition)
        self.assertFalse(self.cnv.has_converged())

        kratios = {29: (0.15, 0.0), 79: (0.85, 0.0)}
        composition = {29: 0.4999, 79: 0.5101}
        self.cnv.add_iteration(kratios, composition)
        self.assertFalse(self.cnv.has_converged())

        kratios = {29: (0.199, 0.0), 79: (0.801, 0.0)}
        composition = {29: 0.4999, 79: 0.5101}
        self.cnv.add_iteration(kratios, composition)
        self.assertTrue(self.cnv.has_converged())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
