#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import os
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.detector import PhotonSpectrumDetector
from pymontecarlo.io.penelope.epma.importer import Importer

import DrixUtilities.Files as Files

# Globals and constants variables.

class TestImporter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        relativePath = os.path.join('../../../testdata/penelope/epma/test1')
        self.testdata = Files.getCurrentModulePath(__file__, relativePath)

        self.i = Importer()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test_detector_photon_spectrum(self):
        # Create
        ops = Options(name='test1')
        ops.beam.energy_eV = 20e3
        ops.detectors['xray1'] = \
            PhotonSpectrumDetector((radians(35), radians(45)), (0, radians(360.0)),
                                   (0, 20e3), 1000)
        ops.detectors['xray2'] = \
            PhotonSpectrumDetector((radians(-35), radians(-45)), (0, radians(360.0)),
                                   (0, 20e3), 1000)

        # Import
        results = self.i.import_from_dir(ops, self.testdata)

        # Test
        self.assertEqual(2, len(results))

        result = results['xray1']

        val, unc = result.intensity('W Ma1')
        self.assertAlmostEqual(6.07152e-05, val, 9)
        self.assertAlmostEqual(2.23e-06, unc, 9)

        val, unc = result.intensity('W Ma1', fluorescence=False)
        self.assertAlmostEqual(5.437632e-05, val, 9)
        self.assertAlmostEqual(2.12e-06, unc, 9)

        val, unc = result.intensity('W Ma1', absorption=False)
        self.assertAlmostEqual(5.521557e-4, val, 9)
        self.assertAlmostEqual(4.79e-06, unc, 9)

        val, unc = result.intensity('W Ma1', absorption=False, fluorescence=False)
        self.assertAlmostEqual(4.883132e-4, val, 9)
        self.assertAlmostEqual(4.45e-06, unc, 9)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
