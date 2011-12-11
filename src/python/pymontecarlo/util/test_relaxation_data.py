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
from pymontecarlo.util.relaxation_data import relaxation_data

# Globals and constants variables.

class TestRelaxationData(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
#
    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testReadData(self):
        self.assertEquals(97, len(relaxation_data.data))
#
    def testenergy(self):
        # Test Al Ka1.
        self.assertEquals(1.48671e3, relaxation_data.energy(13, [4, 1]))

    def testprobability(self):
        # Test Al Ka1.
        self.assertEquals(2.45528e-2, relaxation_data.probability(13, [4, 1]))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
