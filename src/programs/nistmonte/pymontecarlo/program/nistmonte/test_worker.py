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

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.options import Options
from pymontecarlo.options.material import Material
from pymontecarlo.options.detector import TimeDetector
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.particle import ELECTRON

from pymontecarlo.program.nistmonte.config import program
from pymontecarlo.program.nistmonte.worker import Worker
from pymontecarlo.program.nistmonte.converter import Converter

# Globals and constants variables.

class TestWorker(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.outputdir = tempfile.mkdtemp()
        self.workdir = tempfile.mkdtemp()

        ops = Options('test')
        ops.beam.origin_m = (0.0, 0.0, 0.001)
        ops.geometry.body.material = \
            Material({79: 1.0}, absorption_energy_eV={ELECTRON: 56.0})
        ops.detectors['time'] = TimeDetector()
        ops.limits.add(ShowersLimit(1))
        self.ops = Converter().convert(ops)[0]

        self.worker = Worker(program)

    def tearDown(self):
        TestCase.tearDown(self)
        shutil.rmtree(self.outputdir, ignore_errors=True)
        shutil.rmtree(self.workdir, ignore_errors=True)

    def testrun(self):
        results = self.worker.run(self.ops, self.outputdir, self.workdir)
        self.assertIn('time', results)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
