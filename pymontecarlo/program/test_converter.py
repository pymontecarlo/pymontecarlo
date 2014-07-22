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
from pymontecarlo.program.converter import Converter

from pymontecarlo.options.options import Options
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.beam import PencilBeam, GaussianBeam
from pymontecarlo.options.geometry import Substrate, Inclusion
from pymontecarlo.options.material import Material
from pymontecarlo.options.detector import TimeDetector, ElectronFractionDetector
from pymontecarlo.options.limit import ShowersLimit, TimeLimit
from pymontecarlo.options.model import \
    (ELASTIC_CROSS_SECTION, MASS_ABSORPTION_COEFFICIENT,
     UserDefinedMassAbsorptionCoefficientModel)

# Globals and constants variables.

class MockConverter(Converter):

    PARTICLES = [ELECTRON]
    MATERIALS = [Material]
    BEAMS = [PencilBeam]
    GEOMETRIES = [Substrate]
    DETECTORS = [TimeDetector]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION: [ELASTIC_CROSS_SECTION.rutherford],
              MASS_ABSORPTION_COEFFICIENT: [MASS_ABSORPTION_COEFFICIENT.henke1993,
                                            UserDefinedMassAbsorptionCoefficientModel]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION: ELASTIC_CROSS_SECTION.rutherford,
                      MASS_ABSORPTION_COEFFICIENT: MASS_ABSORPTION_COEFFICIENT.henke1993}

class TestConverter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options()
        self.ops.beam = PencilBeam(15e3)
        self.ops.geometry = Substrate(Material.pure(29))
        self.ops.detectors['det1'] = TimeDetector()
        self.ops.limits.add(ShowersLimit(5678))
        self.ops.models.add(ELASTIC_CROSS_SECTION.rutherford)
        self.ops.models.add(MASS_ABSORPTION_COEFFICIENT.henke1993)

        self.converter = MockConverter()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        opss = self.converter.convert(self.ops)
        self.assertEqual(1, len(opss))

    def test_convert_beam(self):
        self.ops.beam = [PencilBeam(15e3), PencilBeam(10e3)]
        opss = self.converter.convert(self.ops)
        self.assertEqual(2, len(opss))

        self.ops.beam = [PencilBeam(15e3), GaussianBeam(10e3, 100e-9)]

        opss = self.converter.convert(self.ops)

        self.assertEqual(1, len(opss))

    def test_convert_geometry(self):
        self.ops.geometry = [Substrate(Material.pure(29)),
                             Inclusion(Material.pure(29), Material.pure(30), 10e-6)]

        opss = self.converter.convert(self.ops)

        self.assertEqual(1, len(opss))

    def test_convert_detector(self):
        self.ops.detectors['det2'] = ElectronFractionDetector()

        opss = self.converter.convert(self.ops)

        self.assertEqual(1, len(opss))
        self.assertEqual(2, len(self.ops.detectors))
        self.assertEqual(1, len(opss[0].detectors))

    def test_convert_limit(self):
        self.ops.limits.add(TimeLimit(123))

        opss = self.converter.convert(self.ops)

        self.assertEqual(1, len(opss))
        self.assertEqual(2, len(self.ops.limits))
        self.assertEqual(1, len(opss[0].limits))

    def test_convert_models(self):
        self.ops.models.add(ELASTIC_CROSS_SECTION.rutherford_relativistic)
        self.ops.models.add(UserDefinedMassAbsorptionCoefficientModel(MASS_ABSORPTION_COEFFICIENT.henke1993))

        opss = self.converter.convert(self.ops)

        self.assertEqual(4, len(opss))
        self.assertEqual(4, len(self.ops.models))
        self.assertEqual(2, len(opss[0].models))

        self.ops.models.add(ELASTIC_CROSS_SECTION.elsepa2005)

        opss = self.converter.convert(self.ops)

        self.assertEqual(6, len(opss))
        self.assertEqual(5, len(self.ops.models))
        self.assertEqual(2, len(opss[0].models))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
