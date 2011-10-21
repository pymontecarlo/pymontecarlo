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
import math

# Third party modules.

# Local modules.
from pymontecarlo.input.beam import PencilBeam, GaussianBeam

# Globals and constants variables.

class TestPencilBeam(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.beam = PencilBeam(15e3, (1, 2, 3), (4, 5, 6), math.radians(3.5))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(15e3, self.beam.energy, 4)

        self.assertAlmostEqual(1.0, self.beam.origin[0], 4)
        self.assertAlmostEqual(2.0, self.beam.origin[1], 4)
        self.assertAlmostEqual(3.0, self.beam.origin[2], 4)

        self.assertAlmostEqual(4.0, self.beam.direction[0], 4)
        self.assertAlmostEqual(5.0, self.beam.direction[1], 4)
        self.assertAlmostEqual(6.0, self.beam.direction[2], 4)

        self.assertAlmostEqual(math.radians(3.5), self.beam.aperture, 4)

    def testfrom_xml(self):
        element = self.beam.to_xml()
        beam = PencilBeam.from_xml(element)

        self.assertAlmostEqual(15e3, beam.energy, 4)

        self.assertAlmostEqual(1.0, beam.origin[0], 4)
        self.assertAlmostEqual(2.0, beam.origin[1], 4)
        self.assertAlmostEqual(3.0, beam.origin[2], 4)

        self.assertAlmostEqual(4.0, beam.direction[0], 4)
        self.assertAlmostEqual(5.0, beam.direction[1], 4)
        self.assertAlmostEqual(6.0, beam.direction[2], 4)

        self.assertAlmostEqual(math.radians(3.5), beam.aperture, 4)

    def testto_xml(self):
        element = self.beam.to_xml()

        self.assertEqual('PencilBeam', element.tag)

        self.assertAlmostEqual(15e3, float(element.get('energy')), 4)

        child = element.find('origin')
        self.assertAlmostEqual(1.0, float(child.get('x')), 4)
        self.assertAlmostEqual(2.0, float(child.get('y')), 4)
        self.assertAlmostEqual(3.0, float(child.get('z')), 4)

        child = element.find('direction')
        self.assertAlmostEqual(4.0, float(child.get('x')), 4)
        self.assertAlmostEqual(5.0, float(child.get('y')), 4)
        self.assertAlmostEqual(6.0, float(child.get('z')), 4)

        self.assertAlmostEqual(math.radians(3.5), float(element.get('aperture')), 4)

class TestGaussianBeam(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.beam = GaussianBeam(15e3, 123.456, (1, 2, 3), (4, 5, 6), math.radians(3.5))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(123.456, self.beam.diameter, 4)

    def testfrom_xml(self):
        element = self.beam.to_xml()
        beam = GaussianBeam.from_xml(element)

        self.assertAlmostEqual(123.456, beam.diameter, 4)

    def testto_xml(self):
        element = self.beam.to_xml()

        self.assertEqual('GaussianBeam', element.tag)

        self.assertAlmostEqual(123.456, float(element.get('diameter')), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
