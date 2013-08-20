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
import tempfile
import shutil
from math import radians as d2r

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.input.options import Options
from pymontecarlo.input.beam import PencilBeam
from pymontecarlo.input.detector import PhotonIntensityDetector
from pymontecarlo.input.limit import ShowersLimit
from pymontecarlo.input.particle import ELECTRON

from pymontecarlo.program.monaco.config import program
from pymontecarlo.program.monaco.runner.worker import Worker
from pymontecarlo.program.monaco.input.converter import Converter

# Globals and constants variables.

class TestWorker(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.outputdir = tempfile.mkdtemp()
        self.workdir = tempfile.mkdtemp()

        ops = Options('test')
        ops.beam = PencilBeam(5e3)
        ops.geometry.material.absorption_energy_eV[ELECTRON] = 56.0
        ops.detectors['xray'] = \
            PhotonIntensityDetector.annular(d2r(40.0), d2r(5.0))
        ops.limits.add(ShowersLimit(1))
        self.ops = Converter().convert(ops)[0]

        self.worker = Worker(program)

    def tearDown(self):
        TestCase.tearDown(self)
        shutil.rmtree(self.outputdir, ignore_errors=True)
        shutil.rmtree(self.workdir, ignore_errors=True)

    def testrun(self):
        results = self.worker.run(self.ops, self.outputdir, self.workdir)
        self.assertIn('time', results[0])

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()