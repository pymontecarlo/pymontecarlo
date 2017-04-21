#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.beam.base import \
    Beam, convert_diameter_fwhm_to_sigma, convert_diameter_sigma_to_fwhm
from pymontecarlo.options.particle import Particle

# Globals and constants variables.

class Testbase(TestCase):

    def testconvert_diameter_fwhm_to_sigma(self):
        self.assertAlmostEqual(0.849321, convert_diameter_fwhm_to_sigma(1.0), 4)

    def testconvert_diameter_sigma_to_fwhm(self):
        self.assertAlmostEqual(1.0, convert_diameter_sigma_to_fwhm(0.849321), 4)

class TestBase(TestCase):

    def setUp(self):
        super().setUp()

        self.b = Beam(15e3, Particle.POSITRON)

    def testskeleton(self):
        self.assertAlmostEqual(15e3, self.b.energy_eV, 4)
        self.assertAlmostEqual(15.0, self.b.energy_keV, 4)
        self.assertEqual(Particle.POSITRON, self.b.particle)

    def test__eq__(self):
        b = Beam(15e3, Particle.POSITRON)
        self.assertEqual(b, self.b)

        b = Beam(15000.009, Particle.POSITRON)
        self.assertEqual(b, self.b)

    def test__ne__(self):
        b = Beam(14e3, Particle.POSITRON)
        self.assertNotEqual(b, self.b)

        b = Beam(15e3, Particle.ELECTRON)
        self.assertNotEqual(b, self.b)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
