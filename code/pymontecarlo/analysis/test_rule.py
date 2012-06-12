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

from pymontecarlo.analysis.rule import ElementByDifferenceRule, FixedElementRule

# Globals and constants variables.

class TestElementByDifferenceRule(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.rule = ElementByDifferenceRule(79)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testupdate(self):
        composition = {29:0.4}
        self.rule.update(composition)

        self.assertAlmostEqual(0.4, composition[29], 4)
        self.assertAlmostEqual(0.6, composition[79], 4)

class TestFixedElementRule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.rule = FixedElementRule(79, 0.2)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def testupdate(self):
        composition = {29:0.4}
        self.rule.update(composition)

        self.assertAlmostEqual(0.4, composition[29], 4)
        self.assertAlmostEqual(0.2, composition[79], 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
