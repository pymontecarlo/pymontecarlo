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
from pyxray.transition import Transition, La

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.limit import TimeLimit, ShowersLimit, UncertaintyLimit

# Globals and constants variables.

class TestTimeLimit(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.lim = TimeLimit(123)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(123, self.lim.time_s)
        self.assertAlmostEqual(2.05, self.lim.time_min, 3)

class TestShowersLimit(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.lim = ShowersLimit(123)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(123, self.lim.showers)

class TestUncertaintyLimit(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        transition = Transition(29, siegbahn='Ka1')
        self.lim = UncertaintyLimit(transition, 0.05)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Cu K\u03b11', str(self.lim.transition))
        self.assertAlmostEqual(0.05, self.lim.uncertainty, 4)

    def testtransitions(self):
        self.lim.transition = list(La(29))
        self.assertEqual(2, len(self.lim.transition))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
