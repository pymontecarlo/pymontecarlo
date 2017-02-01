#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.beam.base import \
    convert_diameter_fwhm_to_sigma, convert_diameter_sigma_to_fwhm

# Globals and constants variables.

class Testbase(TestCase):

    def testconvert_diameter_fwhm_to_sigma(self):
        self.assertAlmostEqual(0.849321, convert_diameter_fwhm_to_sigma(1.0), 4)

    def testconvert_diameter_sigma_to_fwhm(self):
        self.assertAlmostEqual(1.0, convert_diameter_sigma_to_fwhm(0.849321), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
