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
import warnings

# Third party modules.

# Local modules.
from pymontecarlo.options.converter import Converter

from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import PencilBeam, GaussianBeam
from pymontecarlo.options.geometry import Substrate, Inclusion
from pymontecarlo.options.material import pure
from pymontecarlo.options.detector import TimeDetector, ElectronFractionDetector
from pymontecarlo.options.limit import ShowersLimit, TimeLimit
from pymontecarlo.options.model import ELASTIC_CROSS_SECTION

# Globals and constants variables.

warnings.simplefilter("always")

class MockConverter(Converter):

    BEAMS = [PencilBeam]
    GEOMETRIES = [Substrate]
    DETECTORS = [TimeDetector]
    LIMITS = [ShowersLimit]
    MODELS = {ELASTIC_CROSS_SECTION: [ELASTIC_CROSS_SECTION.rutherford]}
    DEFAULT_MODELS = {ELASTIC_CROSS_SECTION: ELASTIC_CROSS_SECTION.rutherford}

class TestConverter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options()
        self.ops.beam = PencilBeam(15e3)
        self.ops.geometry = Substrate(pure(29))
        self.ops.detectors['det1'] = TimeDetector()
        self.ops.limits.add(ShowersLimit(5678))
        self.ops.models.add(ELASTIC_CROSS_SECTION.rutherford)

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

        with warnings.catch_warnings(record=True) as ws:
            opss = self.converter.convert(self.ops)

        self.assertEqual(1, len(ws))
        self.assertEqual(1, len(opss))

    def test_convert_geometry(self):
        self.ops.geometry = [Substrate(pure(29)),
                             Inclusion(pure(29), pure(30), 10e-6)]

        with warnings.catch_warnings(record=True) as ws:
            opss = self.converter.convert(self.ops)

        self.assertEqual(1, len(ws))
        self.assertEqual(1, len(opss))

    def test_convert_detector(self):
        self.ops.detectors['det2'] = ElectronFractionDetector()

        with warnings.catch_warnings(record=True) as ws:
            opss = self.converter.convert(self.ops)

        self.assertEqual(1, len(ws))
        self.assertEqual(1, len(opss))
        self.assertEqual(2, len(self.ops.detectors))
        self.assertEqual(1, len(opss[0].detectors))

    def test_convert_limit(self):
        self.ops.limits.add(TimeLimit(123))

        with warnings.catch_warnings(record=True) as ws:
            opss = self.converter.convert(self.ops)

        self.assertEqual(1, len(ws))
        self.assertEqual(1, len(opss))
        self.assertEqual(2, len(self.ops.limits))
        self.assertEqual(1, len(opss[0].limits))

    def test_convert_models(self):
        self.ops.models.add(ELASTIC_CROSS_SECTION.rutherford_relativistic)

        with warnings.catch_warnings(record=True) as ws:
            opss = self.converter.convert(self.ops)

        self.assertEqual(1, len(ws))
        self.assertEqual(1, len(opss))
        self.assertEqual(2, len(self.ops.models))
        self.assertEqual(1, len(opss[0].models))

if __name__ == '__main__': # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
