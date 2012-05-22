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
from pymontecarlo.testcase import TestCase

from pymontecarlo.input.options import Options
from pymontecarlo.input.limit import TimeLimit
from pymontecarlo.input.detector import \
    PhotonIntensityDetector, PhotonSpectrumDetector, PhiRhoZDetector
from pymontecarlo.program.penepma.input.converter import Converter
from pymontecarlo.program.penepma.io.exporter import Exporter

# Globals and constants variables.

class TestPenelopeExporter(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()

        self.c = Converter()
        self.e = Exporter()

    def tearDown(self):
        TestCase.tearDown(self)

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testskeleton(self):
        self.assertTrue(True)

    def testexport(self):
        # Create
        ops = Options(name='test1')
        ops.detectors['x-ray'] = \
            PhotonIntensityDetector((radians(35), radians(45)), (0, radians(360.0)))
        ops.detectors['spectrum'] = \
            PhotonSpectrumDetector((radians(35), radians(45)), (0, radians(360.0)), (0, 1000), 500)
        ops.detectors['prz'] = \
            PhiRhoZDetector((radians(0), radians(90)), (0, radians(360.0)), 500)
        ops.limits.add(TimeLimit(100))

        # Export
        self.c.convert(ops)
        self.e.export(ops, self.tmpdir)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
