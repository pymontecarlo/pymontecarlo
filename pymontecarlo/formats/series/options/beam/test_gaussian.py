#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.options.beam.gaussian import GaussianBeamSeriesHandler
from pymontecarlo.options.beam.gaussian import GaussianBeam
from pymontecarlo.options.particle import Particle

# Globals and constants variables.

class TestGaussianBeamSeriesHandler(TestCase):

    def testconvert(self):
        handler = GaussianBeamSeriesHandler()
        beam = GaussianBeam(15e3, 123.456, Particle.POSITRON, 1.0, 2.0)
        s = handler.convert(beam)
        self.assertEqual(5, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
