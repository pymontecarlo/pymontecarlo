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

from pymontecarlo.program._penelope.converter import Converter
from pymontecarlo.options.options import Options
from pymontecarlo.options.geometry import Substrate
from pymontecarlo.options.material import Material
from pymontecarlo.options.limit import TimeLimit
from pymontecarlo.options.particle import POSITRON

# Globals and constants variables.

class TestPenelopeConverter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.converter = Converter((0.1, 0.2), 51.2, 53.4)

    def tearDown(self):
        TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test_convert_geometry_substrate(self):
        # Base options
        ops = Options(name="Test")
        mat = Material.pure(29, absorption_energy_eV={POSITRON: 63.4})
        ops.geometry = Substrate(mat)
        ops.limits.add(TimeLimit(100))

        # Convert
        self.converter._convert_geometry(ops)

        # Test
        self.assertEqual('Copper', str(ops.geometry.body.material))

        for material in ops.geometry.get_materials():
            self.assertAlmostEqual(0.1, material.elastic_scattering[0], 4)
            self.assertAlmostEqual(0.2, material.elastic_scattering[1], 4)
            self.assertAlmostEqual(51.2, material.cutoff_energy_inelastic_eV, 4)
            self.assertAlmostEqual(53.4, material.cutoff_energy_bremsstrahlung_eV, 4)
            self.assertAlmostEqual(63.4, material.absorption_energy_eV[POSITRON], 4)
            self.assertAlmostEqual(1e20, material.maximum_step_length_m, 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

