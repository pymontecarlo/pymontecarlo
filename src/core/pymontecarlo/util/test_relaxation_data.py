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
from pymontecarlo.testcase import TestCase

from pymontecarlo.util.relaxation_data import relaxation_data

# Globals and constants variables.

class TestRelaxationData(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)
#
    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testReadData(self):
        self.assertEquals(97, len(relaxation_data.data))
#
    def testenergy_eV(self):
        # Al Ka1.
        self.assertAlmostEquals(1.48671e3, relaxation_data.energy_eV(13, [4, 1]), 4)

        # Li Ka1
        self.assertAlmostEquals(52.0, relaxation_data.energy_eV(3, [4, 1]), 4)

    def testprobability(self):
        # Al Ka1.
        self.assertAlmostEquals(2.45528e-2, relaxation_data.probability(13, [4, 1]), 6)

        # Li Ka1
        self.assertAlmostEquals(1.06e-4, relaxation_data.probability(3, [4, 1]), 6)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
