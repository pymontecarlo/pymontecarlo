#!/usr/bin/env python
"""
================================================================================
:mod:`testcase` -- Common test case for all unit tests
================================================================================

.. module:: testcase
   :synopsis: Common test case for all unit tests

.. inheritance-diagram:: pymontecarlo.testcsse

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import unittest
import math

# Third party modules.

# Local modules.
from pymontecarlo.settings import load_settings, _set_settings
from pymontecarlo.program.base import Program
from pymontecarlo.program.expander import Expander, expand_to_single
from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.limit import ShowersLimit

# Globals and constants variables.

basepath = os.path.dirname(__file__)
filepath = os.path.join(basepath, 'testdata', 'settings.cfg')
settings = load_settings([filepath])

class ExpanderMock(Expander):

    def expand_detectors(self, detectors):
        return expand_to_single(detectors)

    def expand_limits(self, limits):
        return expand_to_single(limits)

    def expand_models(self, models):
        return expand_to_single(models)

    def expand_analyses(self, analyses):
        return expand_to_single(analyses)

class ProgramMock(Program):

    def create_expander(self):
        return ExpanderMock()

    @property
    def name(self):
        return 'mock'

class TestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        _set_settings(settings)

        self.program = ProgramMock()

    def _create_basic_options(self):
        beam = GaussianBeam(15e3, 10e-9)
        sample = SubstrateSample(Material.pure(29))
        detectors = [PhotonDetector(math.radians(40.0))]
        limits = [ShowersLimit(100)]
        models = []
        analyses = []
        return Options(self.program, beam, sample, detectors, limits, models, analyses)

