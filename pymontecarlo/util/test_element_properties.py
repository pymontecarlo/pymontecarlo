#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = ""
__date__ = ""
__copyright__ = "Copyright (c) 2007 Hendrix Demers"
__license__ = ""

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
import pymontecarlo.util.element_properties as ep

# Globals and constants variables.

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testmass_density(self):
        self.assertAlmostEqual(7.1900, ep.mass_density(24))

    def testatomic_mass(self):
        self.assertAlmostEqual(51.996000, ep.atomic_mass(24))

    def testsymbol(self):
        self.assertEquals('Al', ep.symbol(13))

    def testname(self):
        self.assertEquals('Aluminium', ep.name(13))

    def testatomic_number(self):
        self.assertEqual(13, ep.atomic_number(symbol='Al'))
        self.assertEqual(13, ep.atomic_number(name='Aluminium'))

    def testexcitation_energy(self):
        self.assertAlmostEqual(166.0, ep.excitation_energy(13), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)

    unittest.main()
