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
from io import BytesIO
import xml.etree.ElementTree as etree

# Third party modules.
from pyxray.transition import Transition

# Local modules.
from pymontecarlo.fileformat.options.limit import \
    TimeLimitXMLHandler, ShowersLimitXMLHandler, UncertaintyLimitXMLHandler
from pymontecarlo.options.limit import \
    TimeLimit, ShowersLimit, UncertaintyLimit

# Globals and constants variables.

class TestTimeLimitXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = TimeLimitXMLHandler()

        self.obj = TimeLimit(123)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:timeLimit xmlns:mc="http://pymontecarlo.sf.net" time="123.0" />')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual(123, obj.time_s)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertAlmostEqual(123.0, float(element.get('time')), 4)

class TestShowersLimitXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = ShowersLimitXMLHandler()

        self.obj = ShowersLimit(123)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:showersLimit xmlns:mc="http://pymontecarlo.sf.net" showers="123" />')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual(123, obj.showers)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertAlmostEqual(123.0, float(element.get('showers')), 4)

class TestUncertaintyLimitXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = UncertaintyLimitXMLHandler()

        self.obj = UncertaintyLimit(Transition(29, siegbahn='Ka1'), 'det1', 0.05)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:uncertaintyLimit xmlns:mc="http://pymontecarlo.sf.net" detector_key="det1" uncertainty="0.05"><transition dest="1" src="4" z="29" /></mc:uncertaintyLimit>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual('Cu K\u03b11', str(obj.transition))
        self.assertEqual('det1', obj.detector_key)
        self.assertAlmostEqual(0.05, obj.uncertainty, 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        subelement = list(element.findall('transition'))[0]
        self.assertEqual(29, int(subelement.get('z')))
        self.assertEqual(4, int(subelement.get('src')))
        self.assertEqual(1, int(subelement.get('dest')))

        self.assertEqual('det1', element.get('detector_key'))

        self.assertAlmostEqual(0.05, float(element.get('uncertainty')), 4)

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
