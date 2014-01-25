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

# Third party modules.

# Local modules.
from pymontecarlo.program.monaco.importer import Importer

from pymontecarlo.options.options import Options
from pymontecarlo.options.material import Material
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.particle import ELECTRON
from pymontecarlo.options.detector import \
    PhotonIntensityDetector, PhotonDepthDetector

# Globals and constants variables.

class TestImporter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ops = Options('aatest')
        self.ops.beam.energy_eV = 4e3
        self.ops.geometry.material = \
            Material({6: 0.4, 13: 0.6}, absorption_energy_eV={ELECTRON: 234.0})
        self.ops.detectors['xray'] = PhotonIntensityDetector((0, 1), (2, 3))
        self.ops.detectors['prz'] = PhotonDepthDetector((0, 1), (2, 3), 128)
        self.ops.limits.add(ShowersLimit(1234))

        self.i = Importer()

        self._testdata = os.path.join(os.path.dirname(__file__), 'testdata')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testimport_(self):
        jobdir = os.path.join(self._testdata, 'job1')
        results = self.i.import_(self.ops, jobdir)

        self.assertEqual(2, len(results[0]))

        result = results[0]['xray']
        val, unc = result.intensity('Cu La')
        self.assertAlmostEqual(3.473295, val, 4)
        self.assertAlmostEqual(0.0, unc, 4)

        result = results[0]['prz']
        self.assertTrue(result.exists('Au La', True, False))
        self.assertTrue(result.exists('Au Ma', True, False))

        self.assertEqual((128, 3), result.get('Au La').shape)
        self.assertEqual((128, 3), result.get('Au Ma').shape)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
