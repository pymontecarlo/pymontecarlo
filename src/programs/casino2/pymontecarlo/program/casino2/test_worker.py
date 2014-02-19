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
import os
import tempfile
import shutil

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo.options.options import Options
from pymontecarlo.options.detector import ElectronFractionDetector
from pymontecarlo.options.limit import ShowersLimit

from pymontecarlo.program.casino2.config import program
from pymontecarlo.program.casino2.worker import Worker
from pymontecarlo.program.casino2.converter import Converter

# Globals and constants variables.

class TestWorker(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.outputdir = tempfile.mkdtemp()

        ops = Options('test')
        ops.detectors['fraction'] = ElectronFractionDetector()
        ops.limits.add(ShowersLimit(1))
        self.ops = Converter().convert(ops)[0]

        self.worker = Worker(program)

    def tearDown(self):
        TestCase.tearDown(self)
        shutil.rmtree(self.outputdir, ignore_errors=True)

    def testcreate(self):
        filepath = self.worker.create(self.ops, self.outputdir)
        self.assertTrue(os.path.exists(filepath))
        self.assertIn('test.sim', os.listdir(self.outputdir))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
