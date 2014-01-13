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

from pymontecarlo.options.body import Body, Layer
from pymontecarlo.options.material import pure
from pymontecarlo.options.xmlmapper import mapper

# Globals and constants variables.

class TestBody(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.body = Body(pure(29))

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.body.material))

    def testfrom_xml(self):
        element = mapper.to_xml(self.body)
        body = mapper.from_xml(element)

        self.assertEqual('Copper', str(body.material))

    def testto_xml(self):
        element = mapper.to_xml(self.body)

        children = list(element.find('material'))
        self.assertEqual(1, len(children))
        self.assertEqual('Copper', children[0].get('name'))

class TestLayer(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.layer = Layer(pure(29), 123.456)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertAlmostEqual(123.456, self.layer.thickness_m, 4)

    def testfrom_xml(self):
        element = mapper.to_xml(self.layer)
        layer = mapper.from_xml(element)

        self.assertAlmostEqual(123.456, layer.thickness_m, 4)

    def testto_xml(self):
        element = mapper.to_xml(self.layer)

        self.assertAlmostEqual(123.456, float(element.get('thickness')), 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
