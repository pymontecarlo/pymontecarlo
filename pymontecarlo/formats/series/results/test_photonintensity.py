#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.formats.series.results.photonintensity import \
    GeneratedPhotonIntensityResultSeriesHandler, EmittedPhotonIntensityResultSeriesHandler
from pymontecarlo.options.analysis.photonintensity import PhotonIntensityAnalysis
from pymontecarlo.results.photonintensity import GeneratedPhotonIntensityResultBuilder

# Globals and constants variables.

class TestEmittedPhotonIntensityResultSeriesHandler(TestCase):

    def testconvert(self):
        handler = EmittedPhotonIntensityResultSeriesHandler()
        result = self.create_basic_photonintensityresult()
        s = handler.convert(result)
        self.assertEqual(14, len(s))

class TestGeneratedPhotonIntensityResultSeriesHandler(TestCase):

    def testconvert(self):
        handler = GeneratedPhotonIntensityResultSeriesHandler()
        analysis = PhotonIntensityAnalysis(self.create_basic_photondetector())
        b = GeneratedPhotonIntensityResultBuilder(analysis)
        b.add_intensity((29, 'Ka1'), 10.0, 0.1)
        b.add_intensity((29, 'Ka2'), 20.0, 0.2)
        b.add_intensity((29, 'Kb1'), 40.0, 0.5)
        result = b.build()
        s = handler.convert(result)
        self.assertEqual(6, len(s))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
