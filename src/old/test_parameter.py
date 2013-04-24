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

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.reconstruction.parameter import Parameter

from pymontecarlo.input.geometry import Inclusion
from pymontecarlo.input.material import pure

# Globals and constants variables.

class TestParameter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        getter = lambda geometry: geometry.inclusion_diameter_m
        setter = lambda geometry, val: setattr(geometry, 'inclusion_diameter_m', val)
        self.param = Parameter(getter, setter, 200e-9, 150e-9, 300e-9)

    def tearDown(self):
        TestCase.tearDown(self)

    def testgetter(self):
        geometry = Inclusion(pure(29), pure(30), 250e-9)
        self.assertAlmostEqual(250e-9, self.param.getter(geometry), 13)

    def testsetter(self):
        geometry = Inclusion(pure(29), pure(30), 250e-9)
        self.param.setter(geometry, 160e-9)
        self.assertAlmostEqual(160e-9, geometry.inclusion_diameter_m, 13)

    def testinitial_value(self):
        self.assertAlmostEqual(200e-9, self.param.initial_value, 13)

    def testconstraints(self):
        constraints = self.param.constraints
        self.assertAlmostEqual(150e-9, constraints[0], 13)
        self.assertAlmostEqual(300e-9, constraints[1], 13)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
