#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os
import math

# Third party modules.

# Local modules.
from pymontecarlo import unit_registry
from pymontecarlo._settings import Settings
from pymontecarlo.testcase import TestCase
import pymontecarlo.util.physics as physics
from pymontecarlo.exceptions import ProgramNotFound

# Globals and constants variables.

class TestSettings(TestCase):

    def setUp(self):
        super().setUp()

        self.settings = Settings([self.program])

    def testread_write(self):
        filepath = os.path.join(self.create_temp_dir(), 'settings.h5')
        self.settings.write(filepath)

        settings = Settings.read(filepath)
        self.assertEqual(1, len(settings.programs))

    def testget_program(self):
        self.assertEqual(self.program, self.settings.get_program('mock'))
        self.assertRaises(ProgramNotFound, self.settings.get_program, 'foo')

    def testset_preferred_unit(self):
        self.settings.set_preferred_unit(unit_registry.lb)

        q1 = unit_registry.Quantity(1.2, unit_registry.kilogram)
        q2 = self.settings.to_preferred_unit(q1)
        self.assertAlmostEqual(2.645547, q2.magnitude, 4)
        self.assertEqual(unit_registry.lb, q2.units)

    def testset_preferred_unit_length(self):
        self.settings.set_preferred_unit(unit_registry.nanometer)
        q1 = unit_registry.Quantity(1.2, unit_registry.meter)
        q2 = self.settings.to_preferred_unit(q1)
        self.assertAlmostEqual(1.2e9, q2.magnitude, 4)
        self.assertEqual(unit_registry.nanometer, q2.units)

    def testset_preferred_unit_energy(self):
        self.settings.set_preferred_unit(unit_registry.joule)
        q1 = unit_registry.Quantity(1.2, unit_registry.electron_volt)
        q2 = self.settings.to_preferred_unit(q1)
        self.assertAlmostEqual(1.2 * physics.e, q2.magnitude, 4)
        self.assertEqual(unit_registry.joule, q2.units)

    def testset_preferred_unit_angle(self):
        self.settings.set_preferred_unit(unit_registry.radian)
        q1 = unit_registry.Quantity(1.2, unit_registry.degree)
        q2 = self.settings.to_preferred_unit(q1)
        self.assertAlmostEqual(math.radians(1.2), q2.magnitude, 4)
        self.assertEqual(unit_registry.radian, q2.units)

    def testset_preferred_unit_density(self):
        self.settings.set_preferred_unit(unit_registry.kilogram / unit_registry.meter ** 3)
        q1 = unit_registry.Quantity(1.2, unit_registry.gram / unit_registry.centimeter ** 3)
        q2 = self.settings.to_preferred_unit(q1)
        self.assertAlmostEqual(1.2e3, q2.magnitude, 4)
        self.assertEqual(unit_registry.kilogram / unit_registry.meter ** 3, q2.units)

    def testclear_preferred_units(self):
        self.settings.set_preferred_unit(unit_registry.nanometer)
        q1 = unit_registry.Quantity(1.2, unit_registry.meter)
        q2 = self.settings.to_preferred_unit(q1)
        self.assertAlmostEqual(1.2e9, q2.magnitude, 4)
        self.assertEqual(unit_registry.nanometer, q2.units)

        self.settings.clear_preferred_units()
        q2 = self.settings.to_preferred_unit(q1)
        self.assertAlmostEqual(1.2, q2.magnitude, 4)
        self.assertEqual(unit_registry.meter, q2.units)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
