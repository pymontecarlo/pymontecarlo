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
from pymontecarlo.input.penelope.body import Body, Layer
from pymontecarlo.input.penelope.material import pure

# Globals and constants variables.

class TestPenelopeBody(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.body = Body(pure(29), 123.45)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.body.material))
        self.assertAlmostEqual(123.45, self.body.maximum_step_length_m, 4)

    def testfrom_xml(self):
        element = self.body.to_xml()
        body = Body.from_xml(element)

        self.assertEqual('Copper', str(body.material))
        self.assertAlmostEqual(123.45, body.maximum_step_length_m, 4)

    def testto_xml(self):
        element = self.body.to_xml()

        children = list(element.find('material'))
        self.assertEqual(1, len(children))
        self.assertEqual('Copper', children[0].get('name'))

        self.assertAlmostEqual(123.45, float(element.get('maximumStepLength')), 4)

class TestPenelopeLayer(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.layer = Layer(pure(29), 56.78, 123.45)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.layer.material))
        self.assertAlmostEqual(56.78, self.layer.thickness_m, 4)
        self.assertAlmostEqual(123.45, self.layer.maximum_step_length_m, 4)

    def testfrom_xml(self):
        element = self.layer.to_xml()
        layer = Layer.from_xml(element)

        self.assertEqual('Copper', str(layer.material))
        self.assertAlmostEqual(56.78, layer.thickness_m, 4)
        self.assertAlmostEqual(123.45, layer.maximum_step_length_m, 4)

    def testto_xml(self):
        element = self.layer.to_xml()

        children = list(element.find('material'))
        self.assertEqual(1, len(children))
        self.assertEqual('Copper', children[0].get('name'))

        self.assertAlmostEqual(56.78, float(element.get('thickness')), 4)

        self.assertAlmostEqual(123.45, float(element.get('maximumStepLength')), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
