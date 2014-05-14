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
from pymontecarlo.util.parameter import \
    (ParameterizedMetaclass, Parameter, Alias,
     AngleParameter, UnitParameter, TimeParameter,
     ParameterizedMutableMapping, ParameterizedMutableSet,
     ParameterizedMutableSequence,
     range_validator, enum_validator,
     iter_parameters, iter_values,
     freeze, expand)

# Globals and constants variables.

class MockParameterization(object, metaclass=ParameterizedMetaclass):

    param1 = Parameter(doc="Parameter 1")
    param2 = Alias(param1, doc="Parameter 2")
    param3 = Parameter(float, range_validator(0.0), doc='Parameter 3')
    param4 = Parameter(str, enum_validator(['a', 'b', 'c']), doc='Parameter 4')
    param5 = AngleParameter(doc="Parameter 5")
    param6 = UnitParameter("m", doc='Parameter 6')
    param7 = TimeParameter(doc='Parameter 7')
    param8 = Parameter(fields=['x', 'y', 'z'], doc='Parameter 8')
    param9 = UnitParameter('A', fields=['a', 'b'], doc='Parameter 8')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<ParameterizedObject(%s)>' % self.name

class TestParameter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.obj = MockParameterization('obj')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(8, len(self.obj.__parameters__))

    def testparam1(self):
        self.assertRaises(AttributeError, getattr, self.obj, 'param1')

        self.obj.param1 = 4.0
        self.assertAlmostEqual(4.0, self.obj.param1, 4)

        subobj = MockParameterization('subobj1')
        self.obj.param1 = subobj
        self.assertIs(subobj, self.obj.param1)

        subobj2 = MockParameterization('subobj2')
        self.obj.param1 = [subobj, subobj2]
        self.assertEqual(2, len(self.obj.param1))
        self.assertIs(subobj, self.obj.param1[0])
        self.assertIs(subobj2, self.obj.param1[1])

        self.obj.param1 = [4.0, 5.0]
        self.assertEqual(2, len(self.obj.param1))
        self.assertAlmostEqual(4.0, self.obj.param1[0], 4)
        self.assertAlmostEqual(5.0, self.obj.param1[1], 4)

        self.obj.__parameters__['param1'].freeze(self.obj)
        self.assertFalse(self.obj.param1.flags.writeable)
        self.assertRaises(ValueError, setattr, self.obj, 'param1', None)

    def testparam1_2(self):
        self.obj.__parameters__['param1'].freeze(self.obj)
        self.assertRaises(ValueError, setattr, self.obj, 'param1', None)

    def testparam2(self):
        self.obj.param1 = 4.0
        self.assertAlmostEqual(4.0, self.obj.param1, 4)
        self.assertAlmostEqual(4.0, self.obj.param2, 4)

        self.obj.param2 = [4.0, 5.0]
        self.assertEqual(2, len(self.obj.param1))
        self.assertAlmostEqual(4.0, self.obj.param1[0], 4)
        self.assertAlmostEqual(5.0, self.obj.param1[1], 4)
        self.assertEqual(2, len(self.obj.param2))
        self.assertAlmostEqual(4.0, self.obj.param2[0], 4)
        self.assertAlmostEqual(5.0, self.obj.param2[1], 4)

        self.obj.param2[1] = 6.0
        self.assertAlmostEqual(4.0, self.obj.param1[0], 4)
        self.assertAlmostEqual(6.0, self.obj.param1[1], 4)

        self.obj.__parameters__['param1'].freeze(self.obj)
        self.assertRaises(ValueError, setattr, self.obj, 'param1', None)
        self.assertRaises(ValueError, setattr, self.obj, 'param2', None)

    def testparam3(self):
        self.obj.param3 = 99
        self.assertEqual(99, self.obj.param3)

        self.assertRaises(ValueError, setattr, self.obj, 'param3', -1)

    def testparam4(self):
        self.obj.param4 = 'a'
        self.assertEqual('a', self.obj.param4)

        self.assertRaises(ValueError, setattr, self.obj, 'param4', 'd')
#
    def testparam5(self):
        self.obj.param5_rad = 0.6
        self.assertAlmostEqual(0.6, self.obj.param5_rad, 4)
        self.assertAlmostEqual(math.degrees(0.6), self.obj.param5_deg, 4)

        self.obj.param5_deg = 0.7
        self.assertAlmostEqual(math.radians(0.7), self.obj.param5_rad, 4)
        self.assertAlmostEqual(0.7, self.obj.param5_deg, 4)

        self.assertFalse(hasattr(self.obj, 'parm5'))
#
    def testparam6(self):
        self.obj.param6_m = 4.567
        self.assertAlmostEqual(4.567, self.obj.param6_m, 4)
        self.assertAlmostEqual(4567.0, self.obj.param6_mm, 4)
        self.assertAlmostEqual(0.004567, self.obj.param6_km, 8)

        self.obj.param6_cm = 89.65
        self.assertAlmostEqual(0.8965, self.obj.param6_m, 4)
        self.assertAlmostEqual(896.5, self.obj.param6_mm, 4)
        self.assertAlmostEqual(0.0008965, self.obj.param6_km, 8)

    def testparam7(self):
        self.obj.param7_day = 1.0
        self.assertAlmostEqual(86400, self.obj.param7_s, 4)
        self.assertAlmostEqual(24, self.obj.param7_hr, 4)

    def testparam8(self):
        self.obj.param8 = (1.0, 2.0, 3.0)
        self.assertAlmostEqual(1.0, self.obj.param8[0], 4)
        self.assertAlmostEqual(2.0, self.obj.param8[1], 4)
        self.assertAlmostEqual(3.0, self.obj.param8[2], 4)
        self.assertAlmostEqual(1.0, self.obj.param8.x, 4)
        self.assertAlmostEqual(2.0, self.obj.param8.y, 4)
        self.assertAlmostEqual(3.0, self.obj.param8.z, 4)

        self.obj.param8 = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
        self.assertEqual(3, len(self.obj.param8))
        self.assertAlmostEqual(1.0, self.obj.param8[0].x, 4)
        self.assertAlmostEqual(2.0, self.obj.param8[0].y, 4)
        self.assertAlmostEqual(3.0, self.obj.param8[0].z, 4)
        self.assertAlmostEqual(4.0, self.obj.param8[1].x, 4)
        self.assertAlmostEqual(5.0, self.obj.param8[1].y, 4)
        self.assertAlmostEqual(6.0, self.obj.param8[1].z, 4)
        self.assertAlmostEqual(7.0, self.obj.param8[2].x, 4)
        self.assertAlmostEqual(8.0, self.obj.param8[2].y, 4)
        self.assertAlmostEqual(9.0, self.obj.param8[2].z, 4)
        self.assertAlmostEqual(1.0, self.obj.param8.x[0], 4)
        self.assertAlmostEqual(4.0, self.obj.param8.x[1], 4)
        self.assertAlmostEqual(7.0, self.obj.param8.x[2], 4)
        self.assertAlmostEqual(2.0, self.obj.param8.y[0], 4)
        self.assertAlmostEqual(5.0, self.obj.param8.y[1], 4)
        self.assertAlmostEqual(8.0, self.obj.param8.y[2], 4)
        self.assertAlmostEqual(3.0, self.obj.param8.z[0], 4)
        self.assertAlmostEqual(6.0, self.obj.param8.z[1], 4)
        self.assertAlmostEqual(9.0, self.obj.param8.z[2], 4)

        self.obj.param8.x[0] = 5.0
        self.assertAlmostEqual(5.0, self.obj.param8[0].x, 4)
        self.assertAlmostEqual(5.0, self.obj.param8.x[0], 4)

    def testparam9(self):
        self.obj.param9_A = (1.0, 2.0)
        self.assertAlmostEqual(1.0, self.obj.param9_A[0], 4)
        self.assertAlmostEqual(2.0, self.obj.param9_A[1], 4)
        self.assertAlmostEqual(1.0e3, self.obj.param9_mA[0], 4)
        self.assertAlmostEqual(2.0e3, self.obj.param9_mA[1], 4)

        self.obj.param9_kA = [(1.0, 2.0), (3.0, 4.0)]
        self.assertAlmostEqual(1.0, self.obj.param9_kA[0].a, 4)
        self.assertAlmostEqual(2.0, self.obj.param9_kA[0].b, 4)
        self.assertAlmostEqual(3.0, self.obj.param9_kA[1].a, 4)
        self.assertAlmostEqual(4.0, self.obj.param9_kA[1].b, 4)
        self.assertAlmostEqual(1.0e3, self.obj.param9_A[0].a, 4)
        self.assertAlmostEqual(2.0e3, self.obj.param9_A[0].b, 4)
        self.assertAlmostEqual(3.0e3, self.obj.param9_A[1].a, 4)
        self.assertAlmostEqual(4.0e3, self.obj.param9_A[1].b, 4)
        self.assertAlmostEqual(1.0e3, self.obj.param9_A.a[0], 4)
        self.assertAlmostEqual(2.0e3, self.obj.param9_A.b[0], 4)
        self.assertAlmostEqual(3.0e3, self.obj.param9_A.a[1], 4)
        self.assertAlmostEqual(4.0e3, self.obj.param9_A.b[1], 4)

    def testiter_parameters(self):
        self.obj.param3 = [98, 99]
        subobj1 = MockParameterization('subobj1')
        subobj1.param1 = [88, 108]
        self.obj.param1 = subobj1

        items = list(iter_parameters(self.obj))
        self.assertEqual(len(self.obj.__parameters__) * 2, len(items))

        filter_items = list(filter(lambda item: item[0] == self.obj, items))
        self.assertEqual(len(self.obj.__parameters__), len(filter_items))

        filter_items = list(filter(lambda item: item[0] == subobj1, items))
        self.assertEqual(len(self.obj.__parameters__), len(filter_items))

    def testiter_values(self):
        subobj1 = MockParameterization('subobj1')
        subobj1.param1 = [88, 108]
        self.obj.param1 = subobj1

        items = list(iter_values(self.obj))

        self.assertEqual(2, len(items))
        for i in range(2):
            self.assertEqual('param1', items[i][1])

    def testiter_values2(self):
        subobj1 = MockParameterization('subobj1')
        subobj1.param1 = [88, 108]
        self.obj.param1 = subobj1
        self.obj.param3 = [98, 99]

        items = list(iter_values(self.obj))
        self.assertEqual(4, len(items))
#
    def testfreeze(self):
        subobj1 = MockParameterization('subobj1')
        subobj1.param1 = [88, 108]
        self.obj.param1 = subobj1

        freeze(self.obj)

        self.assertRaises(ValueError, setattr, self.obj, 'param1', 0)
        self.assertRaises(ValueError, setattr, self.obj, 'param2', 0)
        self.assertRaises(ValueError, setattr, self.obj, 'param3', 0)
        self.assertRaises(ValueError, setattr, self.obj, 'param4', 0)

        self.assertRaises(ValueError, setattr, self.obj.param1, 'param1', 0)
        self.assertRaises(ValueError, setattr, self.obj.param1, 'param2', 0)
        self.assertRaises(ValueError, setattr, self.obj.param1, 'param3', 0)
        self.assertRaises(ValueError, setattr, self.obj.param1, 'param4', 0)

    def testfreeze2(self):
        subobj1 = MockParameterization('subobj1')
        subobj1.attr1 = [88, 108]
        self.obj.param1 = subobj1

        freeze(self.obj.param1)

        self.obj.attr1 = 0.0

        self.assertRaises(ValueError, setattr, self.obj.param1, 'param1', 0)
        self.assertRaises(ValueError, setattr, self.obj.param1, 'param2', 0)
        self.assertRaises(ValueError, setattr, self.obj.param1, 'param3', 0)
        self.assertRaises(ValueError, setattr, self.obj.param1, 'param4', 0)

    def testexpand(self):
        subobj1 = MockParameterization('subobj1')
        subobj1.param1 = [88, 108]
        self.obj.param1 = subobj1

        objs = expand(self.obj)

        self.assertEqual(2, len(objs))

        self.assertEqual([88, 108], self.obj.param1.param1.tolist())
        self.assertEqual(88, objs[0].param1.param1)
        self.assertEqual(108, objs[1].param1.param1)

    def testexpand2(self):
        self.obj.param8 = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]

        objs = expand(self.obj)

        self.assertEqual(3, len(objs))

        self.assertAlmostEqual(1.0, objs[0].param8[0], 4)
        self.assertAlmostEqual(4.0, objs[1].param8[0], 4)
        self.assertAlmostEqual(7.0, objs[2].param8[0], 4)

    def testparametrized_mutable_mapping(self):
        d = ParameterizedMutableMapping()
        d['a'] = [1.0, 4.0, 9.0]
        d['b'] = 6.0
        self.obj.param1 = d

        self.assertEqual(len(self.obj.__parameters__) + 2,
                         len(list(iter_parameters(self.obj))))
        self.assertEqual(4, len(list(iter_values(self.obj))))
        self.assertEqual(3, len(expand(self.obj)))

    def testparametrized_mutable_set(self):
        s = ParameterizedMutableSet()
        s.add(4.0)
        self.obj.param1 = s

        self.assertEqual(len(self.obj.__parameters__) + 1,
                         len(list(iter_parameters(self.obj))))
        self.assertEqual(1, len(list(iter_values(self.obj))))

    def testparametrized_mutable_sequence(self):
        s = ParameterizedMutableSequence()
        s.append((4.0, 5.0))
        self.obj.param1 = s

        self.assertEqual(len(self.obj.__parameters__),
                         len(list(iter_parameters(self.obj))))
        self.assertEqual(2, len(list(iter_values(self.obj))))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
