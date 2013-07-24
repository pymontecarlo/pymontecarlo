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

from pymontecarlo.input.particle import ELECTRON
from pymontecarlo.input.collision import DELTA
from pymontecarlo.input.xmlmapper import mapper

from pymontecarlo.program._penelope.input.body import Body, Layer
from pymontecarlo.program._penelope.input.material import pure
from pymontecarlo.program._penelope.input.interactionforcing import InteractionForcing

# Globals and constants variables.

class TestBody(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.body = Body(pure(29), 123.45)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.body.material))
        self.assertAlmostEqual(123.45, self.body.maximum_step_length_m, 4)

    def testfrom_xml(self):
        element = mapper.to_xml(self.body)
        body = mapper.from_xml(element)

        self.assertEqual('Copper', str(body.material))
        self.assertAlmostEqual(123.45, body.maximum_step_length_m, 4)

    def testto_xml(self):
        element = mapper.to_xml(self.body)

        children = list(element.find('material'))
        self.assertEqual(1, len(children))
        self.assertEqual('Copper', children[0].get('name'))

        self.assertAlmostEqual(123.45, float(element.get('maximum_step_length')), 4)

class TestLayer(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.layer = Layer(pure(29), 56.78, 123.45)

        intforce = InteractionForcing(ELECTRON, DELTA, -5)
        self.layer.interaction_forcings.add(intforce)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual('Copper', str(self.layer.material))
        self.assertAlmostEqual(56.78, self.layer.thickness_m, 4)
        self.assertAlmostEqual(123.45, self.layer.maximum_step_length_m, 4)
        self.assertEqual(1, len(self.layer.interaction_forcings))

    def testfrom_xml(self):
        element = mapper.to_xml(self.layer)
        layer = mapper.from_xml(element)

        self.assertEqual('Copper', str(layer.material))
        self.assertAlmostEqual(56.78, layer.thickness_m, 4)
        self.assertAlmostEqual(123.45, layer.maximum_step_length_m, 4)
        self.assertEqual(1, len(layer.interaction_forcings))

    def testto_xml(self):
        element = mapper.to_xml(self.layer)

        children = list(element.find('material'))
        self.assertEqual(1, len(children))
        self.assertEqual('Copper', children[0].get('name'))

        self.assertAlmostEqual(56.78, float(element.get('thickness')), 4)

        self.assertAlmostEqual(123.45, float(element.get('maximum_step_length')), 4)

if __name__ == '__main__':  #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
