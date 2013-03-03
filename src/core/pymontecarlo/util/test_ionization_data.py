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

from pymontecarlo.util.ionization_data import ionization_data

# Globals and constants variables.

class TestIonizationData(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)
#
    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testReadData(self):
        self.assertEquals(99, len(ionization_data.data))
#
    def testenergy_eV(self):
        # Test Al K.
        self.assertAlmostEquals(1.564e3, ionization_data.energy_eV(13, 1), 4)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
