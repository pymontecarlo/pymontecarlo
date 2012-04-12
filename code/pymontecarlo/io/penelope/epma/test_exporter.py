#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import tempfile
import shutil
from math import radians

# Third party modules.

# Local modules.
from pymontecarlo.input.base.options import Options
from pymontecarlo.input.base.limit import TimeLimit
from pymontecarlo.input.base.detector import PhotonIntensityDetector
from pymontecarlo.input.penelope.epma.converter import Converter
from pymontecarlo.io.penelope.epma.exporter import Exporter

# Globals and constants variables.

class TestPenelopeExporter(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

        self.c = Converter()
        self.e = Exporter()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    def testexport(self):
        # Create
        ops = Options(name='test1')
        ops.detectors['x-ray'] = \
            PhotonIntensityDetector((radians(35), radians(45)), (0, radians(360.0)))
        ops.limits.add(TimeLimit(100))

        # Export
        self.c.convert(ops)
        self.e.export(ops, self.tmpdir)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
