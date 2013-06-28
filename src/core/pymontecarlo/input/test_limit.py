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

from pymontecarlo.input.limit import TimeLimit, ShowersLimit, UncertaintyLimit

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

#    def testfrom_xml(self):
#        element = self.lim.to_xml()
#        lim = TimeLimit.from_xml(element)
#
#        self.assertEqual(123, lim.time_s)
#
#    def testto_xml(self):
#        element = self.lim.to_xml()
#
#        self.assertEqual(123, int(element.get('time')))

class TestShowersLimit(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.lim = ShowersLimit(123)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(123, self.lim.showers)

#    def testfrom_xml(self):
#        element = self.lim.to_xml()
#        lim = ShowersLimit.from_xml(element)
#
#        self.assertEqual(123, lim.showers)
#
#    def testto_xml(self):
#        element = self.lim.to_xml()
#
#        self.assertEqual(123, int(element.get('showers')))

class TestUncertaintyLimit(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        transition = Transition(29, siegbahn='Ka1')
        self.lim = UncertaintyLimit(transition, 0.05)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(1, len(self.lim.transitions))
        self.assertEqual('Cu Ka1', str(list(self.lim.transitions)[0]))
        self.assertAlmostEqual(0.05, self.lim.uncertainty, 4)

    def testtransitions(self):
        self.lim.transitions.update(La(29))
        self.assertEqual(3, len(self.lim.transitions))

#    def testfrom_xml(self):
#        element = self.lim.to_xml()
#        lim = UncertaintyLimit.from_xml(element)
#
#        self.assertEqual(1, len(self.lim.transitions))
#        self.assertEqual('Cu Ka1', str(list(self.lim.transitions)[0]))
#        self.assertAlmostEqual(0.05, lim.uncertainty, 4)
#
#    def testto_xml(self):
#        element = self.lim.to_xml()
#
#        child = list(element)[0]
#        self.assertEqual(29, int(child.get('z')))
#        self.assertEqual(4, int(child.get('src')))
#        self.assertEqual(1, int(child.get('dest')))
#
#        self.assertAlmostEqual(0.05, float(element.get('uncertainty')), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
