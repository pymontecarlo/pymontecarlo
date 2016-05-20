#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import math
from io import BytesIO
import xml.etree.ElementTree as etree

# Third party modules.

# Local modules.
from pymontecarlo.fileformat.options.beam import \
    PencilBeamXMLHandler, GaussianBeamXMLHandler, GaussianExpTailBeamXMLHandler
from pymontecarlo.options.beam import PencilBeam, GaussianBeam, GaussianExpTailBeam
from pymontecarlo.options.particle import POSITRON

# Globals and constants variables.

class TestPencilBeamXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = PencilBeamXMLHandler()

        self.obj = PencilBeam(15e3, POSITRON, [(1.0, 2.0, 3.0), (1.5, 2.0, 3.0)],
                              (4.0, 5.0, 6.0), math.radians(3.5))

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:pencilBeam xmlns:mc="http://pymontecarlo.sf.net" aperture="0.061086523819801536" energy="15000.0" particle="positron"><origin x="1.0,1.5" y="2.0,2.0" z="3.0,3.0" /><direction u="4" v="5" w="6" /></mc:pencilBeam>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual(POSITRON, obj.particle)

        self.assertAlmostEqual(15e3, obj.energy_eV, 4)
        self.assertAlmostEqual(15.0, obj.energy_keV, 4)

        self.assertAlmostEqual(1.0, obj.origin_m.x[0], 4)
        self.assertAlmostEqual(1.5, obj.origin_m.x[1], 4)
        self.assertAlmostEqual(2.0, obj.origin_m.y[0], 4)
        self.assertAlmostEqual(2.0, obj.origin_m.y[1], 4)
        self.assertAlmostEqual(3.0, obj.origin_m.z[0], 4)
        self.assertAlmostEqual(3.0, obj.origin_m.z[1], 4)

        self.assertAlmostEqual(4.0, obj.direction.u, 4)
        self.assertAlmostEqual(5.0, obj.direction.v, 4)
        self.assertAlmostEqual(6.0, obj.direction.w, 4)

        self.assertAlmostEqual(math.radians(3.5), obj.aperture_rad, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertEqual('15000.0', element.get('energy'))
        self.assertEqual('positron', element.get('particle'))
        self.assertEqual('1.0,1.5', element.find('origin').get('x'))
        self.assertEqual('2.0,2.0', element.find('origin').get('y'))
        self.assertEqual('3.0,3.0', element.find('origin').get('z'))
        self.assertEqual('4.0', element.find('direction').get('u'))
        self.assertEqual('5.0', element.find('direction').get('v'))
        self.assertEqual('6.0', element.find('direction').get('w'))
        self.assertTrue(element.get('aperture').startswith('0.0610865'))

class TestGaussianBeamXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = GaussianBeamXMLHandler()

        self.obj = GaussianBeam(15e3, 123.456, POSITRON, (1.0, 2.0, 3.0),
                                (4.0, 5.0, 6.0), math.radians(3.5))

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:gaussianBeam xmlns:mc="http://pymontecarlo.sf.net" aperture="0.061086523819801536" diameter="123.456" energy="15000.0" particle="positron"><origin x="1.0" y="2" z="3" /><direction u="4" v="5" w="6" /></mc:gaussianBeam>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(123.456, obj.diameter_m, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertEqual('123.456', element.get('diameter'))

class TestGaussianExpTailBeamXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = GaussianExpTailBeamXMLHandler()

        self.obj = GaussianExpTailBeam(15e3, 123.456, 0.1, 1.0,
                                       POSITRON, (1.0, 2.0, 3.0),
                                       (4.0, 5.0, 6.0), math.radians(3.5))

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:gaussianExpTailBeam xmlns:mc="http://pymontecarlo.sf.net" aperture="0.061086523819801536" diameter="123.456" energy="15000.0" particle="positron" skirtThreshold="0.1" skirtFactor="1.0"><origin x="1.0" y="2" z="3" /><direction u="4" v="5" w="6" /></mc:gaussianExpTailBeam>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertAlmostEqual(0.1, obj.skirt_threshold, 4)
        self.assertAlmostEqual(1.0, obj.skirt_factor, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertEqual('0.1', element.get('skirtThreshold'))
        self.assertEqual('1.0', element.get('skirtFactor'))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

