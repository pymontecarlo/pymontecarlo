#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import math

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
import pymontecarlo.util.units as units
import pymontecarlo.util.physics as physics

# Globals and constants variables.

class Testunits(TestCase):

    def testset_preferred_unit(self):
        units.set_preferred_unit(units.ureg.lb)

        q1 = units.ureg.Quantity(1.2, units.ureg.kilogram)
        q2 = units.to_preferred_unit(q1)
        self.assertAlmostEqual(2.645547, q2.magnitude, 4)
        self.assertEqual(units.ureg.lb, q2.units)

    def testset_preferred_unit_length(self):
        units.set_preferred_unit(units.ureg.nanometer)
        q1 = units.ureg.Quantity(1.2, units.ureg.meter)
        q2 = units.to_preferred_unit(q1)
        self.assertAlmostEqual(1.2e9, q2.magnitude, 4)
        self.assertEqual(units.ureg.nanometer, q2.units)

    def testset_preferred_unit_energy(self):
        units.set_preferred_unit(units.ureg.joule)
        q1 = units.ureg.Quantity(1.2, units.ureg.electron_volt)
        q2 = units.to_preferred_unit(q1)
        self.assertAlmostEqual(1.2 * physics.e, q2.magnitude, 4)
        self.assertEqual(units.ureg.joule, q2.units)

    def testset_preferred_unit_angle(self):
        units.set_preferred_unit(units.ureg.radian)
        q1 = units.ureg.Quantity(1.2, units.ureg.degree)
        q2 = units.to_preferred_unit(q1)
        self.assertAlmostEqual(math.radians(1.2), q2.magnitude, 4)
        self.assertEqual(units.ureg.radian, q2.units)

    def testset_preferred_unit_density(self):
        units.set_preferred_unit(units.ureg.kilogram / units.ureg.meter ** 3)
        q1 = units.ureg.Quantity(1.2, units.ureg.gram / units.ureg.centimeter ** 3)
        q2 = units.to_preferred_unit(q1)
        self.assertAlmostEqual(1.2e3, q2.magnitude, 4)
        self.assertEqual(units.ureg.kilogram / units.ureg.meter ** 3, q2.units)

    def testclear_preferred_units(self):
        units.set_preferred_unit(units.ureg.nanometer)
        q1 = units.ureg.Quantity(1.2, units.ureg.meter)
        q2 = units.to_preferred_unit(q1)
        self.assertAlmostEqual(1.2e9, q2.magnitude, 4)
        self.assertEqual(units.ureg.nanometer, q2.units)

        units.clear_preferred_units()
        q2 = units.to_preferred_unit(q1)
        self.assertAlmostEqual(1.2, q2.magnitude, 4)
        self.assertEqual(units.ureg.meter, q2.units)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
