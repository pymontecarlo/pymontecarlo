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
from pymontecarlo.settings import Settings, XrayNotation
from pymontecarlo.testcase import TestCase
import pymontecarlo.util.physics as physics

# Globals and constants variables.

class TestSettings(TestCase):

    def setUp(self):
        super().setUp()

        self.settings = Settings()

    def testread_write(self):
        self.settings.preferred_xray_notation = XrayNotation.SIEGBAHN
        self.settings.set_preferred_unit('nm')

        filepath = os.path.join(self.create_temp_dir(), 'settings.h5')
        self.settings.write(filepath)

        settings = Settings.read(filepath)
        self.assertEqual(XrayNotation.SIEGBAHN, settings.preferred_xray_notation)
        self.assertEqual(unit_registry.nanometer, settings.to_preferred_unit(1.0, unit_registry.meter).units)

    def testset_preferred_unit(self):
        self.settings.set_preferred_unit(unit_registry.lb)

        q = self.settings.to_preferred_unit(1.2, unit_registry.kilogram)
        self.assertAlmostEqual(2.645547, q.magnitude, 4)
        self.assertEqual(unit_registry.lb, q.units)

    def testset_preferred_unit_length(self):
        self.settings.set_preferred_unit(unit_registry.nanometer)

        q = self.settings.to_preferred_unit(1.2, unit_registry.meter)
        self.assertAlmostEqual(1.2e9, q.magnitude, 4)
        self.assertEqual(unit_registry.nanometer, q.units)

    def testset_preferred_unit_energy(self):
        self.settings.set_preferred_unit(unit_registry.joule)

        q = self.settings.to_preferred_unit(1.2, unit_registry.electron_volt)
        self.assertAlmostEqual(1.2 * physics.e, q.magnitude, 4)
        self.assertEqual(unit_registry.joule, q.units)

    def testset_preferred_unit_angle(self):
        self.settings.set_preferred_unit(unit_registry.radian)

        q = self.settings.to_preferred_unit(1.2, unit_registry.degree)
        self.assertAlmostEqual(math.radians(1.2), q.magnitude, 4)
        self.assertEqual(unit_registry.radian, q.units)

    def testset_preferred_unit_density(self):
        self.settings.set_preferred_unit(unit_registry.kilogram / unit_registry.meter ** 3)

        q = self.settings.to_preferred_unit(1.2, unit_registry.gram / unit_registry.centimeter ** 3)
        self.assertAlmostEqual(1.2e3, q.magnitude, 4)
        self.assertEqual(unit_registry.kilogram / unit_registry.meter ** 3, q.units)

    def testclear_preferred_units(self):
        self.settings.set_preferred_unit(unit_registry.nanometer)

        q = self.settings.to_preferred_unit(1.2, unit_registry.meter)
        self.assertAlmostEqual(1.2e9, q.magnitude, 4)
        self.assertEqual(unit_registry.nanometer, q.units)

        self.settings.clear_preferred_units()

        q = self.settings.to_preferred_unit(q)
        self.assertAlmostEqual(1.2, q.magnitude, 4)
        self.assertEqual(unit_registry.meter, q.units)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
