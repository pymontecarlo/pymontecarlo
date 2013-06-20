#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.input.parameter import \
    (ParameterizedMetaClass, Parameter, SimpleValidator,
     ParameterAlias, AngleParameter, UnitParameter,
     iter_parameters, iter_values, freeze, expand,
     ParameterizedMutableMapping, ParameterizedMutableSet)

# Globals and constants variables.

class ParametrizedObject(object):

    __metaclass__ = ParameterizedMetaClass

    param1 = Parameter(doc="Parameter 1")
    param2 = Parameter(SimpleValidator(lambda x: x > 0), doc='Parameter 2')
    param3 = Parameter(doc='Parameter 3')
    param4 = ParameterAlias(param1, doc="Parameter 4")
    param5 = AngleParameter(doc="Parameter5")
    param6 = UnitParameter("m", doc='Parameter6 (in meters)')

    def __init__(self, name):
        self.name = name

        self.param3 = 99
        self.__parameters__['param3'].freeze(self)

    def __repr__(self):
        return '<ParameterizedObject(%s)>' % self.name

class TestParameter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.obj = ParametrizedObject('obj')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(5, len(self.obj.__parameters__))

    def testparam1(self):
        self.assertRaises(AttributeError, getattr, self.obj, 'param1')

        self.obj.param1 = 6
        self.assertEqual(6, self.obj.param1)

        self.obj.param1 = [6, 5, 7]
        self.assertEqual((6, 5, 7), self.obj.param1)

    def testparam2(self):
        self.assertRaises(ValueError, setattr, self.obj, 'param2', -1)
        self.assertRaises(ValueError, setattr, self.obj, 'param2', [2, 3, -1])
        
    def testparam3(self):
        self.assertEqual(99, self.obj.param3)

        self.assertRaises(AttributeError, setattr, self.obj, 'param3', 1)

    def testparam4(self):
        self.obj.param1 = 6
        self.assertEqual(6, self.obj.param1)
        self.assertEqual(6, self.obj.param4)

        self.obj.param4 = 7
        self.assertEqual(7, self.obj.param1)
        self.assertEqual(7, self.obj.param4)

    def testparam5(self):
        self.obj.param5_rad = 0.6
        self.assertAlmostEqual(0.6, self.obj.param5_rad, 4)
        self.assertAlmostEqual(math.degrees(0.6), self.obj.param5_deg, 4)

        self.obj.param5_deg = 0.7
        self.assertAlmostEqual(math.radians(0.7), self.obj.param5_rad, 4)
        self.assertAlmostEqual(0.7, self.obj.param5_deg, 4)

    def testparam6(self):
        self.obj.param6_m = 4.567
        self.assertAlmostEqual(4.567, self.obj.param6_m, 4)
        self.assertAlmostEqual(4567.0, self.obj.param6_mm, 4)
        self.assertAlmostEqual(0.004567, self.obj.param6_km, 8)

        self.obj.param6_cm = 89.65
        self.assertAlmostEqual(0.8965, self.obj.param6_m, 4)
        self.assertAlmostEqual(896.5, self.obj.param6_mm, 4)
        self.assertAlmostEqual(0.0008965, self.obj.param6_km, 8)

    def testiter_parameters(self):
        subobj1 = ParametrizedObject('subobj1')
        subobj1.param1 = [88, 108]
        self.obj.param1 = [subobj1]
        
        self.assertEqual(10, len(list(iter_parameters(self.obj))))

    def testiter_values(self):
        subobj1 = ParametrizedObject('subobj1')
        subobj1.param1 = [88, 108]
        self.obj.param1 = [subobj1]

        self.assertEqual(4, len(list(iter_values(self.obj))))
        self.assertEqual(2, len(list(iter_values(self.obj, keep_frozen=False))))

    def testfreeze(self):
        subobj1 = ParametrizedObject('subobj1')
        subobj1.param1 = [88, 108]
        self.obj.param1 = [subobj1]

        freeze(self.obj)

        self.assertRaises(AttributeError, setattr, self.obj, 'param1', 0)
        self.assertRaises(AttributeError, setattr, self.obj, 'param2', 0)
        self.assertRaises(AttributeError, setattr, self.obj, 'param3', 0)
        self.assertRaises(AttributeError, setattr, self.obj, 'param4', 0)
        self.assertRaises(AttributeError, setattr, self.obj, 'param5_rad', 0)
        self.assertRaises(AttributeError, setattr, self.obj, 'param6_m', 0)
        self.assertRaises(AttributeError, setattr, self.obj, 'param6_mm', 0)

        self.assertRaises(AttributeError, setattr, self.obj.param1, 'param1', 0)
        self.assertRaises(AttributeError, setattr, self.obj.param1, 'param2', 0)
        self.assertRaises(AttributeError, setattr, self.obj.param1, 'param3', 0)
        self.assertRaises(AttributeError, setattr, self.obj.param1, 'param4', 0)
        self.assertRaises(AttributeError, setattr, self.obj.param1, 'param5_rad', 0)
        self.assertRaises(AttributeError, setattr, self.obj.param1, 'param6_m', 0)
        self.assertRaises(AttributeError, setattr, self.obj.param1, 'param6_mm', 0)

    def testexpand(self):
        subobj1 = ParametrizedObject('subobj1')
        subobj1.param1 = [88, 108]
        self.obj.param1 = [subobj1]

        objs = expand(self.obj)

        self.assertEqual(2, len(objs))

        self.assertEqual((88, 108), self.obj.param1.param1)
        self.assertEqual(88, objs[0].param1.param1)
        self.assertEqual(108, objs[1].param1.param1)

    def testparametrized_mutable_mapping(self):
        d = ParameterizedMutableMapping()
        d['a'] = [1.0, 4.0, 9.0]
        d[0] = [6]
        self.obj.param1 = d

        self.assertEqual(7, len(list(iter_parameters(self.obj))))
        self.assertEqual(4, len(list(iter_values(self.obj, keep_frozen=False))))

    def testparametrized_mutable_set(self):
        s = ParameterizedMutableSet()
        s.add(4.0)
        self.obj.param1 = s

        self.assertEqual(6, len(list(iter_parameters(self.obj))))
        self.assertEqual(1, len(list(iter_values(self.obj, keep_frozen=False))))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
