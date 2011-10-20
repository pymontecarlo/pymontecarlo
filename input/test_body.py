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
from pymontecarlo.input.body import Body, Layer
from pymontecarlo.input.material import pure

# Globals and constants variables.

class TestBody(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.body = Body(pure(29))

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.body.material))

    def testfrom_xml(self):
        element = self.body.to_xml()
        body = Body.from_xml(element)

        self.assertEqual('Copper', str(body.material))

    def testto_xml(self):
        element = self.body.to_xml()

        self.assertEqual('Body', element.tag)

        children = list(element.find('material'))
        self.assertEqual(1, len(children))
        self.assertEqual('Copper', children[0].get('name'))

class TestLayer(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.layer = Layer(pure(29), 123.456)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(123.456, self.layer.thickness, 4)

    def testfrom_xml(self):
        element = self.layer.to_xml()
        layer = Layer.from_xml(element)

        self.assertAlmostEqual(123.456, layer.thickness, 4)

    def testto_xml(self):
        element = self.layer.to_xml()

        self.assertEqual('Layer', element.tag)

        self.assertAlmostEqual(123.456, float(element.get('thickness')), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
