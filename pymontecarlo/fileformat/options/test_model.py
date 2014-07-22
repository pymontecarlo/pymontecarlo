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
import xml.etree.ElementTree as etree
from io import BytesIO

# Third party modules.
from pyxray.transition import Transition

# Local modules.
from pymontecarlo.fileformat.options.model import \
    (_ModelXMLHandler, RegisteredModelXMLHandler,
     UserDefinedMassAbsorptionCoefficientModelXMLHandler)

from pymontecarlo.options.model import \
    (ModelType, _Model, UserDefinedMassAbsorptionCoefficientModel,
     MASS_ABSORPTION_COEFFICIENT)

# Globals and constants variables.

MTYPE = ModelType('type1')
try:
    MTYPE.m1 = ('name1', 'ref1')
    MTYPE.m2 = ('name2',)
except ValueError:
    pass # Already imported

class TestModelXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = _ModelXMLHandler()

        self.obj1 = _Model(MTYPE, 'name1', 'ref1')
        self.obj2 = _Model(MTYPE, 'name2')

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:_model xmlns:mc="http://pymontecarlo.sf.net" name="name1" type="type1" reference="ref1" />')
        self.element1 = etree.parse(source).getroot()

        source = BytesIO(b'<mc:_model xmlns:mc="http://pymontecarlo.sf.net" name="name2" type="type1" />')
        self.element2 = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element1))
        self.assertTrue(self.h.can_parse(self.element2))

    def testparse(self):
        # Model 1
        obj = self.h.parse(self.element1)

        self.assertEqual('name1', obj.name)
        self.assertEqual('ref1', obj.reference)
        self.assertEqual(MTYPE, obj.type)

        # Model 2
        obj = self.h.parse(self.element2)

        self.assertEqual('name2', obj.name)
        self.assertEqual('', obj.reference)
        self.assertEqual(MTYPE, obj.type)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj1))
        self.assertTrue(self.h.can_convert(self.obj2))

    def testconvert(self):
        # Model 1
        element = self.h.convert(self.obj1)

        self.assertEqual('name1', element.get('name'))
        self.assertEqual(str(MTYPE), element.get('type'))

        # Model 2
        element = self.h.convert(self.obj2)

        self.assertEqual('name2', element.get('name'))
        self.assertEqual(str(MTYPE), element.get('type'))

class TestRegisteredModelXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = RegisteredModelXMLHandler()

        self.obj1 = MTYPE.m1
        self.obj2 = MTYPE.m2

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:model xmlns:mc="http://pymontecarlo.sf.net" name="name1" type="type1" />')
        self.element1 = etree.parse(source).getroot()

        source = BytesIO(b'<mc:model xmlns:mc="http://pymontecarlo.sf.net" name="name2" type="type1" />')
        self.element2 = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element1))
        self.assertTrue(self.h.can_parse(self.element2))

    def testparse(self):
        # Model 1
        obj = self.h.parse(self.element1)

        self.assertEqual('name1', obj.name)
        self.assertEqual('ref1', obj.reference)
        self.assertEqual(MTYPE, obj.type)

        # Model 2
        obj = self.h.parse(self.element2)

        self.assertEqual('name2', obj.name)
        self.assertEqual('', obj.reference)
        self.assertEqual(MTYPE, obj.type)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj1))
        self.assertTrue(self.h.can_convert(self.obj2))

    def testconvert(self):
        # Model 1
        element = self.h.convert(self.obj1)

        self.assertEqual('name1', element.get('name'))
        self.assertEqual(str(MTYPE), element.get('type'))

        # Model 2
        element = self.h.convert(self.obj2)

        self.assertEqual('name2', element.get('name'))
        self.assertEqual(str(MTYPE), element.get('type'))

class TestUserDefinedMassAbsorptionCoefficientModelXMLHandler(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.h = UserDefinedMassAbsorptionCoefficientModelXMLHandler()

        self.obj = UserDefinedMassAbsorptionCoefficientModel(MASS_ABSORPTION_COEFFICIENT.henke1993, 'ref1')
        self.obj.add(29, 8.904e3, 200)
        self.obj.add(29, Transition(29, siegbahn='Ka1'), 201)

        etree.register_namespace('mc', 'http://pymontecarlo.sf.net')
        source = BytesIO(b'<mc:userDefinedMassAbsorptionCoefficientModel xmlns:mc="http://pymontecarlo.sf.net" name="user defined mass absorption coefficient" reference="ref1" type="mass absorption coefficient"><mc:model name="Henke 1993" reference="B.L. Henke, E.M. Gullikson and J.C. Davis (1993). X-ray interactions: photoabsorption, scattering, transmission, and reflection at E=50-30000 eV, Z=1-92, Atomic Data and Nuclear Data Tables, 54, pp. 181-342" type="mass absorption coefficient" /><mac absorber="29" energy="8904.0">200</mac><mac absorber="29" z="29" src="4" dest="1">201</mac></mc:userDefinedMassAbsorptionCoefficientModel>')
        self.element = etree.parse(source).getroot()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcan_parse(self):
        self.assertTrue(self.h.can_parse(self.element))

    def testparse(self):
        obj = self.h.parse(self.element)

        self.assertEqual('user defined mass absorption coefficient', obj.name)
        self.assertEqual('ref1', obj.reference)
        self.assertEqual(MASS_ABSORPTION_COEFFICIENT, obj.type)

        self.assertIs(MASS_ABSORPTION_COEFFICIENT.henke1993, obj.base_model)

        self.assertEqual(2, len(obj.defined_macs))
        self.assertAlmostEqual(200.0, obj.defined_macs[(29, 8.904e3)], 4)
        self.assertAlmostEqual(201.0, obj.defined_macs[(29, Transition(29, siegbahn='Ka1'))], 4)

    def testcan_convert(self):
        self.assertTrue(self.h.can_convert(self.obj))

    def testconvert(self):
        element = self.h.convert(self.obj)

        self.assertEqual('user defined mass absorption coefficient', element.get('name'))
        self.assertEqual(str(MASS_ABSORPTION_COEFFICIENT), element.get('type'))

        subelement = element.find('{http://pymontecarlo.sf.net}model')
        self.assertEqual('Henke 1993', subelement.get('name'))

        subelements = list(element.iter('mac'))
        self.assertEqual(2, len(subelements))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
